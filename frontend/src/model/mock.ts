
export class Mock {

    resultImages() {
        return [...Array(100).keys()].map ( index => {
            return "https://picsum.photos/seed/" + (index + 1) + "/224"
        })
    }

}


const mock = new Mock();
(window as any).mock = mock;
export default mock;
