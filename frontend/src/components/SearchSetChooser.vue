<template>
    <div class="search-set-dropdown"
      :class="{open: menuOpen}"
      v-on-clickaway="closeMenu">
      <div class="drop-down-button" ref="button" @click="toggleMenu">
        <div class="search-set-icon" :class="{missing: !selectedSearchSet}" />
        <div class="search-set-title"
             v-if="selectedSearchSet"
             v-tooltip.bottom-start="{
              content:
                (selectedSearchSet.name ? selectedSearchSet.name : 'untitled') +
                ' by ' + selectedSearchSet.creatorName,
              offset: 3,
              delay: { show: 1000 },
             }">
          {{ selectedSearchSet.name ? selectedSearchSet.name : 'untitled' }}
        </div>
        <div class="search-set-title" v-else>
          Search set...
        </div>
      </div>

      <div class="drop-menu">
        <ul>
          <li
            v-for="set in searchSets"
            :key="set.vueKey"
            @click="searchSetClicked(set)"
            >
            <div class="tick" :class="{selected: set == selectedSearchSet}" />
            <div class="set-name">
              {{ set.name ? set.name : 'untitled' }} by {{ set.creatorName }}
            </div>
          </li>
          <div class="line" />
          <li @click="newSearchSetClicked()">
            <div class="option">New search set</div>
          </li>
          <li
           v-if="selectedSearchSet.isCustom"
           @click="openSearchSetClicked(selectedSearchSet)">
            <div class="option">Open this search set</div>
          </li>
        </ul>
      </div>
  </div>
</template>

<script>
import {SearchSet} from '../model/SearchSet';
import notificationCenter from "@/model/notificationCenter";
import { mixin as clickaway } from 'vue-clickaway';
import router from '@/router'

export default {
  name: 'SearchSetChooser',
  props: {
    selectedSearchSet: SearchSet,
    searchSets: Array,
    snapshotId: String
  },
  data() {
    return {
      menuOpen: false
    }
  },
  mounted() {
    notificationCenter.$on('context-menu-will-open', this.contextMenuWillOpen)
  },
  beforeDestroy() {
    notificationCenter.$off('context-menu-will-open', this.contextMenuWillOpen)
  },
  methods: {
    toggleMenu(event) {
      this.menuOpen = !this.menuOpen
    },
    closeMenu() {
      this.menuOpen = false
    },
    contextMenuWillOpen(menu) {
      this.menuOpen = false
    },
    searchSetClicked(set) {
      this.$emit('didSelectSearchSet' , set)
      this.closeMenu()
    },
    newSearchSetClicked() {
      router.push({
        name: 'new-search-set',
        params: {fromSnapshotId: this.snapshotId},
      })
    },
    openSearchSetClicked(set) {
      router.push({
        name: 'search-set',
        params: {searchSetId: set.searchSetId, fromSnapshotId: this.snapshotId },
      })
    }
  },
  mixins: [
    clickaway
  ],
}
</script>

<style scoped>
.search-set-dropdown {
  position: relative;
  user-select: none;
  max-width: 40%;
}
.drop-down-button {
  display: flex;
  align-items: center;
  padding: 5px 15px 5px 0px;
  cursor: pointer;
}
.search-set-icon {
  width: 18px;
  height: 18px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(../components/assets/icon_search_set.svg);
  flex-shrink: 0;
}
.drop-down-button:hover .search-set-icon, .open .search-set-icon {
  background-image: url(../components/assets/icon_search_set_active.svg);
}
.search-set-title {
  font-family: Roboto, sans-serif;
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 0.17px;
  margin-left: 6px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  height: 20px;
}
.drop-down-button:hover .search-set-title, .open .search-set-title {
  color: #3B59FF;
}
.open .disclosure {
  transform: rotate(-90deg)
}
.drop-menu {
  position: fixed;
  width: auto;
  opacity: 0;
  pointer-events: none;
  z-index: 100;
  background: #FFFFFF;
  box-shadow: 0 2px 15px -5px rgba(0,0,0,0.50);
  overflow-y: auto;
  transition: all ease 0.2s;
  max-height: 50vh;
}
.open .drop-menu {
  opacity: 1;
  pointer-events: unset;
  transition: all ease 0.0s;
}
.drop-menu ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}
.drop-menu li {
  white-space: nowrap;
  display: flex;
  height: 34px;
  font-weight: 500;
  font-size: 13px;
  color: #5E5E5E;
  letter-spacing: 0.19px;
  align-items: center;
  padding-right: 22px;
  cursor: pointer;
}
.drop-menu li:hover {
  background-color: #3B59FF;
  color: #fff;
  transition: background-color ease 0.15s;
}
.drop-menu .line {
  height: 1px;
  width: 100%;
  background-color: #E8EAED;
}
.set-name {
  margin-left: 7px;
  max-width: 200px;
  text-overflow: ellipsis;
  overflow: hidden;
}
.option {
  margin-left: 27px;
  color: inherit;
  text-decoration: none;
}
.tick {
  width: 12px;
  height: 9px;
  opacity: 0;
  margin-left: 8px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(./assets/icon_tick.svg);
}
.drop-menu li:hover .tick {
  filter: invert(100%) brightness(200%);
}
.tick.selected {
  opacity: 1;
}
.missing {
  opacity: 0.8;
}
</style>
