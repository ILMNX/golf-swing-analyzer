<script lang="ts">
	import { page } from '$app/stores';

	const links = [
		{ href: '/', label: 'Beranda' },
		{ href: '/analyze', label: 'Analisis' },
		{ href: '/report', label: 'Laporan' }
	];
</script>

<header class="border-b border-border bg-obsidian">
	<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
		<a href="/" class="group flex items-center gap-3">
			<svg width="28" height="28" viewBox="0 0 32 32" fill="none" aria-hidden="true">
				<path d="M16 6v18" stroke="#1E7A3D" stroke-width="1.5" stroke-linecap="round"/>
				<path d="M16 6l5 3" stroke="#1E7A3D" stroke-width="1.5" stroke-linecap="round"/>
				<circle cx="16" cy="24" r="2.5" stroke="#A6E3A1" stroke-width="1.5"/>
			</svg>
			<div>
				<p class="font-display text-sm font-bold uppercase tracking-widest text-offwhite">
					SwingLab
				</p>
				<p class="text-[10px] uppercase tracking-widest text-muted">Performance Analysis</p>
			</div>
		</a>

		<nav class="flex items-center">
			{#each links as link}
				<a
					href={link.href}
					class="border-b-2 px-4 py-2 text-xs font-medium uppercase tracking-wider transition
						{$page.url.pathname === link.href
						? 'border-golf text-offwhite'
						: 'border-transparent text-muted hover:text-offwhite'}"
				>
					{link.label}
				</a>
			{/each}
		</nav>
	</div>
</header>
