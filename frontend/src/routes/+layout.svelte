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
	<footer class="border-t border-border py-5">
		<div class="mx-auto max-w-6xl px-4 sm:px-6">
			<p class="text-xs uppercase tracking-widest text-disabled">
				SwingLab &mdash; Golf Swing Analyzer
			</p>
		</div>
	</footer>
</div>
