<template>
	<div id="wrapper">
		<router-view />
	</div>
</template>

<script>
	export default {};
</script>

<style lang="sass">
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

	.flex-row
		flex-direction: row

	.flex-column
		flex-direction: column

	.center
		align-items: center
		justify-content: center
</style>
