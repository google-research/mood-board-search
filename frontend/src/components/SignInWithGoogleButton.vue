<template>
  <button class="sign-in-with-google-button"
          @click="$emit('click')">
  </button>
</template>

<script>
export default {

}
</script>

<style>
.sign-in-with-google-button {
  width: 191px;
  height: 46px;
  border: none;
  background-image: url(./assets/btn_google_signin_light_normal_web@2x.png);
  background-size: cover;
  background-repeat: no-repeat;
}
.sign-in-with-google-button:focus {
  background-image: url(./assets/btn_google_signin_light_focus_web@2x.png);
  outline: none;
}
.sign-in-with-google-button:active {
  background-image: url(./assets/btn_google_signin_light_pressed_web@2x.png);
}
.sign-in-with-google-button[disabled] {
  background-image: url(./assets/btn_google_signin_light_disabled_web@2x.png);
}
</style>
