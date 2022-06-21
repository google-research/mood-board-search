import ResizeObserver from 'resize-observer-polyfill'
import Vue from 'vue';

export default Vue.extend({
    data() {
        return {
            elementSize: {width: 0, height: 0},
            __ObserveSizeMixin__observer: null as ResizeObserver|null,
        }
    },
    mounted() {
        this.__ObserveSizeMixin__update()
        this.__ObserveSizeMixin__observer = new ResizeObserver(entries => {
            this.__ObserveSizeMixin__update()
        })
        this.__ObserveSizeMixin__observer.observe(this.$el);
    },
    beforeDestroy() {
        this.__ObserveSizeMixin__observer?.disconnect()
    },
    methods: {
        __ObserveSizeMixin__update() {
            this.elementSize.width = this.$el.clientWidth;
            this.elementSize.height = this.$el.clientHeight;
        }
    },
})
