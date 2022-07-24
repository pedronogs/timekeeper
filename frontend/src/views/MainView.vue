<template>
	<div id="main">
		<div id="menu">
			<div id="banner">TimeKeeper</div>
			<q-list dark padding class="text-white">
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

		<div id="main-content" class="d-flex flex-row flex-wrap">
			<task-component v-for="task in tasks" :key="task.id" :color="colors[Math.floor(Math.random() * (colors.length + 1))]" class="q-ma-md" :task-data="task" />
			<div id="new-task" class="q-ma-md">
				<q-btn label="Add New Task" color="white" text-color="blue" icon-right="add" size="md" fab @click="promptNewTask = true" />
			</div>
		</div>

		<!-- Dialogs -->

		<!-- Add new task -->
		<q-dialog v-model="promptNewTask" persistent>
			<q-card style="width: 500px">
				<q-card-section>
					<div class="text-h6">Your Python Script</div>
				</q-card-section>

				<q-card-section class="q-pt-none">
					<q-file filled bottom-slots v-model="newTaskFile" label="File" counter accept=".py">
						<template v-slot:prepend>
							<q-icon name="cloud_upload" @click.stop.prevent />
						</template>
						<template v-slot:append>
							<q-icon name="close" @click.stop.prevent="model = null" class="cursor-pointer" />
						</template>

						<template v-slot:hint>
							Add your custom python code
						</template>
					</q-file>
				</q-card-section>

				<q-card-actions align="evenly" class="text-primary">
					<q-btn flat label="Cancel" v-close-popup />
					<q-btn flat label="Create New Task" v-close-popup @click="addNewTask" />
				</q-card-actions>
			</q-card>
		</q-dialog>
	</div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import type { Task } from "../types/types";
import { useQuasar } from "quasar";

import axios from "axios";
import TaskComponent from "../components/TaskComponent.vue";

export default defineComponent({
	name: "MainView",
	components: {
		TaskComponent
	},
	data() {
		return {
			promptNewTask: false as boolean,
			newTaskFile: new Blob as Blob,
			tasks: [] as Array<Task>,
			colors: ["burlywood", "darkolivegreen", "green", "black", "orange", "indigo", "brown", "darkslateblue", "darkslategray", "steelblue", "teal"]
		};
	},
	setup() {
		const $q = useQuasar();

		return {
			triggerNotification(type: string, message: string) {
				$q.notify({
					type: type,
					message: message,
					position: "top-right",
				});
			},
		};
	},
	created() {
		this.getTasks();
	},
	methods: {
		getTasks() {
			axios.get("/api/tasks").then(response => {
				this.tasks = response.data.map((task: { id: string, next_run_time: string, schedule: string }) => {
					return {
						id: task.id,
						schedule: task.schedule,
						nextRunTime: task.next_run_time,
					};
				});
			}).catch(error => {
				this.triggerNotification("negative", error.data.message)
			});
		},
		addNewTask() {
			let newTask = new FormData();
			newTask.append('file', this.newTaskFile);

			axios.post("/api/tasks", newTask, {
				headers: {
					'Content-Type': 'multipart/form-data'
				}
			})
				.then(response => {
					this.triggerNotification("positive", response.data.message)
				})
				.catch(error => {
					this.triggerNotification("negative", error.data.message)
				});
		}
	}
});
</script>

<style lang="sass" scoped>
#main
	width: 100%
	height: 100%
	background-color: #212529

#menu
	width: 300px
	height: 100%

	position: fixed
	left: 0

	background-color: #343a40

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

	align-items: flex-start

	background-color: #212529

	padding: 25px
	padding-left: 325px

#new-task
	width: 355px
	height: 255px

	background-color: transparent

	display: flex
	justify-content: center
	align-items: center
</style>
