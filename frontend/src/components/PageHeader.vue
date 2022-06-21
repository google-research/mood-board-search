<template>
  <div class="page-header margins">
    <div class="page-header-row">
      <router-link :to="{name: 'projects-list'}"><div class="logo" /></router-link>
      <h1 class="page-title" :class="titleClass">{{ title }}</h1>
      <div class="spacer" style="flex: 1"></div>
      <div class="right-button" v-for="(button, index) in rightButtons" :key="index">
        <span v-if="typeof button.action === 'function'"
              @click.prevent.stop="button.action()"
              v-text="button.title"
              class="right-button-inner" />
        <router-link v-else
                     :to="button.action"
                     v-text="button.title"
                     class="right-button-inner" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue'
import { RawLocation } from 'vue-router'

interface RightButton {
  title: string,
  action: (()=>void) | RawLocation
}

export default {
  name: 'PageHeader',
  props: {
    title: String,
    titleClass: Object,
    rightButtons: {
      default: () => [],
      type: Array as PropType<RightButton[]>
    }
  },
}
</script>

<style lang="scss" scoped>
.page-header {
  color: #454545;
}

.page-header-row {
  display: flex;
  align-items: center;
  margin-bottom: 17px;
  margin-top: 25px;
}

.logo {
  width: 108px;
  height: 34px;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(./assets/logo_type.svg);
}

.page-title {
  font-size: 17px;
  margin-bottom: 0;
  margin-left: 15px;

  &.faint {
    color: #b8b8b8;
  }
}

.right-button {
  font-weight: bold;
  font-size: 17px;
  letter-spacing: 0.24px;
  text-align: right;
}
.right-button-inner {
  text-decoration: none;
  cursor: pointer;
  user-select: none;

  &, &:link, &:visited {
    color: inherit;
  }
  &:hover {
    border-bottom: 2px solid currentColor;
  }
}

</style>
