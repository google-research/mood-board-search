#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# set settings for django to work
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cavstudio_backend.settings")

# ensure that cavstudio_backend can be imported
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

import django
from django.apps import apps as django_apps
import tempfile
from urllib.request import urlretrieve
from urllib.parse import urlparse
import shutil
import json
from tqdm import tqdm
import textwrap
from cavstudio_backend.image_reference import precalculate_activations, ImageReference
from django.core.management import call_command as django_call_command

FEATURE_CONCEPTS_URL = 'https://services.google.com/fh/files/misc/featured_concepts_v2.zip'
SCOUT_IMAGES_URL = 'https://services.google.com/fh/files/misc/cavstudio_image_bank_sample_set_v2.zip'

STATIC_CAV_CONTENT_DIR = BACKEND_DIR / 'static-cav-content'


def main():
    print(textwrap.dedent('''
        ##########################
        # CAVstudio setup script #
        ##########################

        This script will download and prepare all the data required to use
        CAVstudio. This comprises the image bank, which provides a dataset for
        your concepts to search, and our featured concepts.

        It will download ~1.1GB of data, and then will preprocess the images
        to create activations. The whole process should take around 10-15
        minutes.

        Please note: the images inside the featured concepts are made publicly
        available for use in CAVstudio only. Copyright is retained by the
        owners of these images.

        Press 'y' followed by 'Enter' to continue.
    '''))

    answer = input('Continue [y/N]: ')

    if answer not in ['Y', 'y']:
        sys.exit('Aborted.')

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = Path(tmpdirname)

        print('------> 1/8 Downloading featured concept archive...')
        concept_archive_filename = os.path.basename(urlparse(FEATURE_CONCEPTS_URL).path)
        concept_archive = temp_dir / concept_archive_filename
        download_file(FEATURE_CONCEPTS_URL, destination=concept_archive)

        print('------> 2/8 Unpacking concept archive...')
        concept_archive_dir = temp_dir / 'featured_concepts'
        concept_archive_dir.mkdir()
        shutil.unpack_archive(concept_archive, extract_dir=concept_archive_dir)

        print('------> 3/8 Downloading image bank archive...')
        scout_archive_filename = os.path.basename(urlparse(SCOUT_IMAGES_URL).path)
        scout_archive = temp_dir / scout_archive_filename
        download_file(SCOUT_IMAGES_URL, destination=scout_archive)

        print('------> 4/8 Unpacking image bank archive...')
        scout_archive_dir = temp_dir / 'scout_images'
        scout_archive_dir.mkdir()
        shutil.unpack_archive(scout_archive, extract_dir=scout_archive_dir)

        print('------> 5/8 Copying files into place...')
        STATIC_CAV_CONTENT_DIR.mkdir(exist_ok=True)
        file_list = list(concept_archive_dir.iterdir()) + list(scout_archive_dir.iterdir())
        image_ids = set()

        # copy all the images
        for file in tqdm(file_list, unit='file'):
            if file.name in ['snapshots.json', 'manifests']:
                continue

            # record image ids so we can compute activations later
            if file.suffix == '.png':
                image_id = file.name.split('.')[0]
                image_ids.add(image_id)

            dst_path = STATIC_CAV_CONTENT_DIR / file.name
            if not dst_path.exists():
                shutil.copy2(src=file, dst=dst_path)

        # copy the image bank manifests
        shutil.copytree(
            src=scout_archive_dir / 'manifests',
            dst=STATIC_CAV_CONTENT_DIR / 'manifests',
            dirs_exist_ok=True,
        )

        print('------> 6/8 Adding concept metadata to database...')
        django.setup()
        django_call_command('migrate')
        Snapshot = django_apps.get_model('cavstudio_db', 'Snapshot')

        snapshots_file = concept_archive_dir / 'snapshots.json'
        snapshots = json.loads(snapshots_file.read_text())

        print('adding featured snapshots...')
        for snapshot in snapshots:
            snapshot['featured'] = True
            Snapshot.objects.update_or_create(id=snapshot['snapshotId'], defaults={'data': snapshot})

        print('------> 7/8 Precomputing activations...')
        image_refs = [ImageReference(id=id, user_generated=False) for id in image_ids]
        # this function shows its own progress bar
        precalculate_activations(image_refs=image_refs)

        print('------> 8/8 Done!')


def download_file(url, destination):
    class TqdmUpTo(tqdm):
        # from tqdm readme
        def update_to(self, b=1, bsize=1, tsize=None):
            if tsize is not None:
                self.total = tsize
            return self.update(b * bsize - self.n)

    url_filename = url.split('/')[-1]

    with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=url_filename) as t:
        urlretrieve(url, filename=destination, reporthook=t.update_to, data=None)

    t.total = t.n


if __name__ == '__main__':
    main()
