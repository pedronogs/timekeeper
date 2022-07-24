<template>
	<q-card class="task d-flex flex-column">
		<q-card-section class="card-header text-white" :style="{'background-color': color}">
			<div class="text-h6">Evaluation</div>
			<div class="text-subtitle2">Task ID: {{ taskData.id }}</div>
		</q-card-section>

		<q-separator inset />

		<q-card-section>
			<span>Last run: 01/01/2001</span><br />
			<span>Last run time: 1h</span><br />
			<span>Last status: Success</span><br />
			<span>Next run scheduled for: {{ formattedRunDate }}</span>
		</q-card-section>

		<q-separator inset />

		<q-card-actions align="around">
			<q-btn flat>Schedule</q-btn>
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
		formattedRunDate() {
			if (this.taskData == undefined || this.taskData.nextRunTime == undefined) {
				return "";
			}

			console.log(this.taskData.nextRunTime)
			return new Date(this.taskData.nextRunTime).toLocaleString();
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
