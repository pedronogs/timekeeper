<template>
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
			<q-btn flat>Edit Scheduler</q-btn>
			<q-btn flat>Run NOW!</q-btn>
		</q-card-actions>
	</q-card>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";
import type { Task } from "../types/types";

export default defineComponent({
	name: "TaskComponent",
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
			type: Object as PropType<Task>,
		},
	},
});
</script>

<style lang="sass">
.task
	width: 355px
	height: 255px
	background-color: white
</style>
