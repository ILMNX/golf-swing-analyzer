<script lang="ts">
	import '../app.css';
	import Navbar from '$lib/components/Navbar.svelte';

	let { children } = $props();
</script>

<div class="flex min-h-screen flex-col">
	<Navbar />
	<main class="flex-1">
		{@render children()}
	</main>
	<footer class="border-t border-fairway-800/60 py-6 text-center text-sm text-fairway-500">
		<p>SwingPro &mdash; Golf Swing Analyzer &copy; {new Date().getFullYear()}</p>
	</footer>
</div>
