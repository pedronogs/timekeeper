<template>
	<div>
		<q-card class="task d-flex flex-column">
			<q-card-section class="card-header text-white" :style="{'background-color': color}">
				<div class="text-h6">{{ taskData.name }}</div>
				<div class="text-subtitle2">Task ID: {{ taskData.id }}</div>
			</q-card-section>

			<q-separator inset />

			<q-card-section>
				<span>Last run: {{ lastRunDate }}</span><br />
				<span>Last run time: -</span><br />
				<span>Last status: -</span><br />
				<span>Next run scheduled for: {{ nextRunDate }}</span>
			</q-card-section>

			<q-separator inset />

			<q-card-actions align="around">
				<q-btn flat @click="promptUpdateTask = true">EDIT</q-btn>
				<q-btn flat style="color: red" @click="pauseTask">PAUSE</q-btn>
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
						<q-btn flat label="Delete Task" icon-right="delete" text-color="red" v-close-popup style="margin-left: auto" @click="deleteTask" />
					</div>

				</q-card-section>

				<q-card-section>
					<q-input outlined v-model="updateTaskValue.name" label="Task Name" stack-label />
					<q-input outlined v-model="updateTaskValue.trigger" label="Insert a valid Cron Trigger" stack-label class="q-mt-md" />
				</q-card-section>

				<q-separator></q-separator>

				<q-card-actions align="evenly" class="text-primary">
					<q-btn flat label="Cancel" v-close-popup />

					<q-btn flat label="Confirm" v-close-popup @click="updateTask" />
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
			updateTaskValue: this.taskData as Task
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
			if (this.taskData == undefined || this.taskData.last_run_time == undefined || this.taskData.last_run_time == null) {
				return "-";
			}

			return new Date(this.taskData.last_run_time).toLocaleString()
		},
		nextRunDate() {
			if (this.taskData == undefined || this.taskData.next_run_time == undefined) {
				return "-";
			}

			return new Date(this.taskData.next_run_time).toLocaleString()
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

			axios.put(`/api/tasks/${this.taskData.id}`, { name: this.updateTaskValue.name, trigger: this.updateTaskValue.trigger }).then(() => {
				this.triggerNotification("positive", "Task updated successfully!");
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
