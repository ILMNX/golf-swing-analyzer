<script lang="ts">
	import { onMount } from 'svelte';
	import MetricsGrid from '$lib/components/MetricsGrid.svelte';
	import ScoreGauge from '$lib/components/ScoreGauge.svelte';
	import { loadReport } from '$lib/api';
	import type { SwingAnalysis } from '$lib/types';
	import { CLUB_LABELS, SHOT_LABELS } from '$lib/types';

	let report = $state<SwingAnalysis | null>(null);

	onMount(() => {
		report = loadReport();
	});

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleString('id-ID', {
			day: 'numeric',
			month: 'long',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<section class="mx-auto max-w-4xl px-4 py-10 sm:px-6">
	{#if !report}
		<div class="card text-center py-16">
			<span class="text-5xl">📋</span>
			<h1 class="mt-4 font-display text-2xl font-semibold text-white">Belum Ada Laporan</h1>
			<p class="mx-auto mt-2 max-w-md text-fairway-400">
				Anda belum melakukan analisis swing. Upload video Anda untuk mendapatkan laporan lengkap.
			</p>
			<a href="/analyze" class="btn-primary mt-8 inline-flex"> Mulai Analisis </a>
		</div>
	{:else}
		<!-- Header -->
		<div class="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
			<div>
				<p class="text-sm font-medium uppercase tracking-wider text-fairway-500">Laporan Analisis</p>
				<h1 class="font-display text-3xl font-semibold text-white">Hasil Swing Anda</h1>
				<p class="mt-1 text-sm text-fairway-400">{formatDate(report.analyzed_at)}</p>
			</div>
			<a href="/analyze" class="btn-secondary shrink-0 text-sm"> Analisis Baru </a>
		</div>

		<!-- Score + meta -->
		<div class="card mb-6">
			<div class="flex flex-col items-center gap-8 md:flex-row md:items-start">
				<ScoreGauge score={report.score} />

				<div class="flex-1 space-y-4 text-center md:text-left">
					<div class="grid grid-cols-2 gap-4">
						<div class="rounded-xl bg-fairway-950/60 p-4">
							<p class="text-xs uppercase tracking-wider text-fairway-500">Club</p>
							<p class="mt-1 text-lg font-semibold text-white">
								{CLUB_LABELS[report.club] ?? report.club}
							</p>
						</div>
						<div class="rounded-xl bg-fairway-950/60 p-4">
							<p class="text-xs uppercase tracking-wider text-fairway-500">Jenis Pukulan</p>
							<p class="mt-1 text-lg font-semibold text-white">
								{SHOT_LABELS[report.shot_type] ?? report.shot_type}
							</p>
						</div>
						<div class="col-span-2 rounded-xl bg-fairway-950/60 p-4">
							<p class="text-xs uppercase tracking-wider text-fairway-500">File Video</p>
							<p class="mt-1 truncate text-sm font-medium text-fairway-200">{report.filename}</p>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Metrics -->
		<div class="card mb-6">
			<h2 class="mb-4 text-lg font-semibold text-white">Metrik Detail</h2>
			<MetricsGrid metrics={report.metrics} />
		</div>

		<!-- Recommendation -->
		<div class="card border-fairway-600/40">
			<div class="flex items-start gap-4">
				<div
					class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-fairway-700 text-2xl"
				>
					💬
				</div>
				<div>
					<h2 class="text-lg font-semibold text-white">Rekomendasi Coach</h2>
					<p class="mt-2 leading-relaxed text-fairway-300">{report.recommendation}</p>
					<p class="mt-4 text-xs text-fairway-600">
						* Rekomendasi akan semakin akurat setelah logika ML YOLOv8-pose diimplementasikan
						sepenuhnya.
					</p>
				</div>
			</div>
		</div>

		<!-- Actions -->
		<div class="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
			<a href="/analyze" class="btn-primary"> Analisis Swing Lain </a>
			<a href="/" class="btn-secondary"> Kembali ke Beranda </a>
		</div>
	{/if}
</section>
