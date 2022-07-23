<template>
	<div id="main">
		<div id="menu">
			<div id="banner">TimeKeeper</div>
			<q-list bordered dark padding class="rounded-borders text-white">
				<q-item dark clickable v-ripple :active="link === 'inbox'" @click="link = 'inbox'" active-class="my-menu-link">
					<q-item-section avatar>
						<q-icon name="schedule" />
					</q-item-section>

					<q-item-section>Tasks</q-item-section>
				</q-item>

				<q-item dark clickable v-ripple :active="link === 'inbox'" @click="link = 'inbox'" active-class="my-menu-link">
					<q-item-section avatar>
						<q-icon name="assessment" />
					</q-item-section>

					<q-item-section>Charts</q-item-section>
				</q-item>
			</q-list>
		</div>

		<div id="main-content">
			<q-card class="tasks-content">
				<q-card-section class="card-header text-white">
					<div class="text-h6">Our Changing Planet</div>
					<div class="text-subtitle2">by John Doe</div>
				</q-card-section>

				<q-card-actions align="around">
					<q-btn flat>Action 1</q-btn>
					<q-btn flat>Action 2</q-btn>
				</q-card-actions>
			</q-card>
		</div>
	</div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
	name: "MainView"
});
</script>

<style lang="sass" scoped>
$first-color: #212529
$second-color: #343a40
$third-color: #495057
$fourth-color: #6c757d
$fifth-color: #ced4da

#main
	width: 100%
	height: 100%
	background-color: $first-color

#menu
	width: 300px
	height: 100%

	position: fixed
	left: 0

	background-color: $second-color

#banner
	height: 120px
	width: 100%

	display: flex
	flex-direction: column
	align-items: center
	justify-content: center

	color: white
	font-weight: bolder
	font-size: 20px

	background-color: #03071e

#main-content
	width: 100%
	height: 100%
	margin-left: 300px
	background-color: $first-color

.tasks-content
	width: 30%
	height: auto
	background-color: $fifth-color

	.card-header
		background-color: $third-color
</style>
