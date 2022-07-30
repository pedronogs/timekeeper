<template>
	<div>
		<q-card class="task d-flex flex-column">
			<q-card-section class="card-header text-white" :style="{'background-color': color}">
				<div class="text-h6">{{ newTaskData.name }}</div>
				<div class="text-subtitle2">Task ID: {{ newTaskData.id }}</div>
			</q-card-section>

			<q-separator inset />

			<q-card-section>
				<span>Last run: {{ lastRunDate }}</span>
				<br />
				<span>Last run time: -</span>
				<br />
				<span>Last status: -</span>
				<br />
				<span>Next run scheduled for: {{ nextRunDate }}</span>
			</q-card-section>

			<q-separator inset />

			<q-card-actions align="around">
				<q-btn flat @click="promptUpdateTask = true">EDIT</q-btn>
				<q-btn
					v-if="newTaskData.next_run_time != null"
					flat
					style="color: red"
					@click="promptPauseTask = true"
				>PAUSE</q-btn>
				<q-btn v-else flat style="color: green" @click="resumeTask">RESUME</q-btn>
				<q-btn flat>Run NOW!</q-btn>
			</q-card-actions>
		</q-card>

		<!-- Dialogs -->
		<!-- Edit task -->
		<q-dialog v-model="promptUpdateTask" persistent>
			<q-card style="width: 500px">
				<q-card-section>
					<div class="d-flex flex-row text-h6">
						<span>Edit Task</span>
						<q-btn
							flat
							label="Delete Task"
							icon-right="delete"
							text-color="red"
							v-close-popup
							style="margin-left: auto"
							@click="promptDeleteTask = true"
						/>
					</div>
				</q-card-section>

				<q-card-section>
					<q-input outlined v-model="updateTaskValue.name" label="Task Name" stack-label />
					<q-input
						outlined
						v-model="updateTaskValue.trigger"
						label="Insert a valid Cron Trigger"
						stack-label
						class="q-mt-md"
					/>
				</q-card-section>

				<q-separator></q-separator>

				<q-card-actions align="evenly" class="text-primary">
					<q-btn flat label="Cancel" v-close-popup />
					<q-btn flat label="Confirm" v-close-popup @click="updateTask" />
				</q-card-actions>
			</q-card>
		</q-dialog>

		<!-- Confirm Deletion -->
		<q-dialog v-model="promptDeleteTask" persistent>
			<q-card>
				<q-card-section class="row items-center">
					<q-icon name="delete" color="red" size="md" />
					<span style="font-size: 1.3rem" class="q-ml-md">
						<strong>Delete Task</strong>
					</span>
				</q-card-section>

				<q-separator />

				<q-card-section class="q-pa-lg text-center" style="font-size: 0.9rem">
					<span>
						Are you
						<strong>completely</strong>
						sure you want to delete this task?
					</span>
					<br />
					<span>ID: {{this.taskData.id}}</span>
				</q-card-section>

				<q-separator />

				<q-card-actions align="evenly">
					<q-btn flat label="Cancel" color="primary" v-close-popup />
					<q-btn flat label="DELETE" color="red" v-close-popup @click="deleteTask" />
				</q-card-actions>
			</q-card>
		</q-dialog>

		<!-- Confirm Pause -->
		<q-dialog v-model="promptPauseTask" persistent>
			<q-card>
				<q-card-section class="row items-center">
					<q-icon name="pause_circle_outline" color="red" size="md" />
					<span style="font-size: 1.3rem" class="q-ml-md">
						<strong>Pause Task</strong>
					</span>
				</q-card-section>

				<q-separator />

				<q-card-section class="q-pa-lg text-center" style="font-size: 0.9rem">
					<span>
						Are you
						<strong>completely</strong>
						sure you want to pause this task?
					</span>
					<br />
					<span>ID: {{this.taskData.id}}</span>
				</q-card-section>

				<q-separator />

				<q-card-actions align="evenly">
					<q-btn flat label="Cancel" color="primary" v-close-popup />
					<q-btn flat label="PAUSE" color="red" v-close-popup @click="pauseTask" />
				</q-card-actions>
			</q-card>
		</q-dialog>
	</div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";
import type { Task } from "../types/types";
import axios from "axios";
import { useQuasar } from "quasar";

export default defineComponent({
	name: "TaskComponent",
	data() {
		return {
			promptUpdateTask: false as boolean,
			promptPauseTask: false as boolean,
			updateTaskValue: { ...this.taskData } as Task,
			promptDeleteTask: false as boolean,
			newTaskData: { ...this.taskData } as Task,
		}
	},
	setup() {
		const $q = useQuasar();

		return {
			triggerNotification(type: string, message: string) {
				$q.notify({
					type: type,
					message: message,
					position: "top-right",
					timeout: 2000
				});
			},
		};
	},
	computed: {
		lastRunDate() {
			if (this.newTaskData == undefined || this.newTaskData.last_run_time == undefined || this.newTaskData.last_run_time == null) {
				return "-";
			}

			return new Date(this.newTaskData.last_run_time).toLocaleString()
		},
		nextRunDate() {
			if (this.newTaskData == undefined || this.newTaskData.next_run_time == undefined) {
				return "-";
			}

			return new Date(this.newTaskData.next_run_time).toLocaleString()
		}
	},
	props: {
		color: {
			type: String,
			default: "grey",
		},
		taskData: {
			type: Object as PropType<Task>
		},
	},
	methods: {
		updateTask() {
			if (this.taskData == undefined) return;

			axios.put(`/api/tasks/${this.taskData.id}`, { name: this.updateTaskValue.name, trigger: this.updateTaskValue.trigger }).then((response) => {
				this.triggerNotification("positive", "Task updated successfully!");
				this.newTaskData = response.data
			}).catch((error) => {
				this.triggerNotification("negative", error.response.data.detail);
			});
		},
		pauseTask() {
			if (this.taskData == undefined) return;

			axios.put(`/api/tasks/${this.taskData.id}/pause`).then((response) => {
				this.triggerNotification("positive", "Task paused!");
				this.newTaskData = response.data
			}).catch((error) => {
				this.triggerNotification("negative", error.response.data.detail);
			});
		},
		resumeTask() {
			if (this.taskData == undefined) return;

			axios.put(`/api/tasks/${this.taskData.id}/resume`).then((response) => {
				this.triggerNotification("positive", "Task resumed!");
				this.newTaskData = response.data
			}).catch((error) => {
				this.triggerNotification("negative", error.response.data.detail);
			});
		},
		deleteTask() {
			if (this.taskData == undefined) return;

			let taskID = this.taskData.id;
			axios.delete(`/api/tasks/${taskID}`).then(() => {
				this.triggerNotification("positive", "Task deleted!");
				this.$emit("deleteTask", taskID);
			}).catch((error) => {
				this.triggerNotification("negative", error.response.data.detail);
			});
		}
	}
});
</script>

<style lang="sass">
.task
	width: 355px
	height: 255px
	background-color: white
</style>
