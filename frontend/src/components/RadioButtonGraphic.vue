<template>
  <svg width="18px" height="18px" viewBox="0 0 18 18" version="1.1">
    <circle :stroke="outlineColor" stroke-width="2" fill="none" cx="9" cy="9" r="8"></circle>
    <circle v-if="selected" :fill="blobColor" cx="9" cy="9" r="4"></circle>
  </svg>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'RadioButtonGraphic',
  props: {
    outlineColor: {
      type: String,
      default: 'currentColor'
    },
    blobColor: {
      type: String,
      default: 'currentColor'
    },
    selected: {
      type: Boolean,
      default: true,
    }
  }
})
</script>
