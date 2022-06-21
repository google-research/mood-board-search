<template>
  <!-- disable native browser drag-drop behaviour on the whole window -->
  <div id="app"
       @dragover.prevent="$event.dataTransfer.dropEffect = 'none'"
       @dragenter.prevent=""
       @drop.prevent="">
    <router-view />
    <modals-container />
    <v-dialog/>
  </div>
</template>

<script>
export default {
  data() {
    return {
    }
  },
  methods: {
  },
  components: {
  }
}
</script>

<style lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
@import './assets/hanken-grotesk/stylesheet.css';
@import './styles.scss';

#app {
  height: 100%;
}
</style>
