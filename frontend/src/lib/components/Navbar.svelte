<script lang="ts">
	import { page } from '$app/stores';
	import { BarChart3, Home, ScanLine } from '@lucide/svelte';

	const links = [
		{ href: '/', label: 'Beranda', icon: Home },
		{ href: '/analyze', label: 'Analisis', icon: ScanLine },
		{ href: '/report', label: 'Laporan', icon: BarChart3 }
	];
</script>

<header class="w-full border-b border-border bg-obsidian">
	<div class="container-page flex items-center justify-between gap-4 py-3 sm:py-4">
		<a href="/" class="flex min-w-0 shrink items-center gap-2 sm:gap-3">
			<svg
				class="shrink-0"
				width="24"
				height="24"
				viewBox="0 0 32 32"
				fill="none"
				aria-hidden="true"
			>
				<path d="M16 6v18" stroke="#1E7A3D" stroke-width="1.5" stroke-linecap="round" />
				<path d="M16 6l5 3" stroke="#1E7A3D" stroke-width="1.5" stroke-linecap="round" />
				<circle cx="16" cy="24" r="2.5" stroke="#A6E3A1" stroke-width="1.5" />
			</svg>
			<div class="min-w-0">
				<p class="truncate font-display text-xs font-bold uppercase tracking-wide text-offwhite sm:text-sm sm:tracking-widest">
					SwingLab
				</p>
				<p class="hidden text-[10px] uppercase tracking-widest text-muted sm:block">
					Performance Analysis
				</p>
			</div>
		</a>

		<nav class="flex shrink-0 items-center">
			{#each links as link}
				{@const Icon = link.icon}
				<a
					href={link.href}
					class="flex items-center gap-1.5 border-b-2 px-2 py-2 text-[10px] font-medium uppercase tracking-wide transition sm:gap-2 sm:px-3 sm:text-xs sm:tracking-wider
						{$page.url.pathname === link.href
						? 'border-golf text-offwhite'
						: 'border-transparent text-muted hover:text-offwhite'}"
				>
					<Icon size={14} strokeWidth={1.5} class="hidden sm:block" />
					<span>{link.label}</span>
				</a>
			{/each}
		</nav>
	</div>
</header>
