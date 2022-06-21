<template>
  <svg class="inspect-spinner" width="50px" height="50px" viewBox="0 0 50 50" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
      <defs>
          <filter x="-52.6%" y="-52.6%" width="202.6%" height="202.6%" filterUnits="objectBoundingBox" id="filter-1">
              <feOffset dx="0" dy="0" in="SourceAlpha" result="shadowOffsetOuter1"></feOffset>
              <feGaussianBlur stdDeviation="4.5" in="shadowOffsetOuter1" result="shadowBlurOuter1"></feGaussianBlur>
              <feColorMatrix values="0 0 0 0 0.490007926   0 0 0 0 0.490007926   0 0 0 0 0.490007926  0 0 0 0.91645542 0" type="matrix" in="shadowBlurOuter1" result="shadowMatrixOuter1"></feColorMatrix>
              <feMerge>
                  <feMergeNode in="shadowMatrixOuter1"></feMergeNode>
                  <feMergeNode in="SourceGraphic"></feMergeNode>
              </feMerge>
          </filter>
      </defs>
      <circle filter="url(#filter-1)" fill="none" stroke="#FFFFFF"
              cx="25" cy="25" r="14" stroke-width="3.6">
      </circle>
      <circle class="rotating"
              fill="none" stroke="#00ffc4"
              cx="25" cy="25" r="14"
              stroke-width="3.6" stroke-dasharray="58.5,29">
      </circle>
  </svg>
</template>

<script>
export default {

}
</script>

<style>
@keyframes rotating {
  from {
    transform: translate(25px, 25px) rotate(0deg) translate(-25px, -25px);
  }
  to {
    transform: translate(25px, 25px) rotate(360deg) translate(-25px, -25px);
  }
}
.rotating {
  animation: rotating 1s linear infinite;
}

</style>
