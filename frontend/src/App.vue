<template>
	<div id="wrapper">
		<router-view />
		<q-ajax-bar ref="bar" position="bottom" color="accent" size="10px" />
	</div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import axios from "axios";

export default defineComponent({
	setup() {
		axios.defaults.baseURL = "http://localhost:8000"
	},
});
</script>

<style lang="sass">
$first-color: #212529
$second-color: #343a40
$third-color: #495057
$fourth-color: #6c757d
$fifth-color: #ced4da

html, body, #app, #wrapper
	width: 100%
	height: 100%
	margin: 0
	padding: 0

#wrapper
	display: flex
	flex-direction: column
	justify-content: center
	align-items: center

.d-flex
	display: flex

.d-inline-flex
	display: inline-flex

.flex-row
	flex-direction: row

.flex-column
	flex-direction: column

.center
	align-items: center
	justify-content: center

.flex-wrap
	flex-wrap: wrap
</style>
