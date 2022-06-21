import Vue from 'vue';

export default Vue.extend({
  data() {
    return {
      altKeyDown: false,
    }
  },
  mounted() {
    window.addEventListener('keydown', this.__AltKeyDownMixin__onKeydown)
    window.addEventListener('keyup', this.__AltKeyDownMixin__onKeyup)
    window.addEventListener('blur', this.__AltKeyDownMixin__blur)
  },
  beforeDestroy() {
    window.removeEventListener('keydown', this.__AltKeyDownMixin__onKeydown)
    window.removeEventListener('keydown', this.__AltKeyDownMixin__onKeyup)
    window.removeEventListener('blur', this.__AltKeyDownMixin__blur)
  },
  methods: {
    __AltKeyDownMixin__onKeydown(event: KeyboardEvent) {
      if (event.keyCode === 18) {
        this.altKeyDown = true;
      }
    },
    __AltKeyDownMixin__onKeyup(event: KeyboardEvent) {
      if (event.keyCode === 18) {
        this.altKeyDown = false;
      }
    },
    __AltKeyDownMixin__blur(event: FocusEvent) {
      this.altKeyDown = false;
    },
  },
})
