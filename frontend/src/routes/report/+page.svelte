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

<section class="mx-auto max-w-6xl px-4 py-10 sm:px-6">
	{#if !report}
		<div class="border border-border bg-graphite px-6 py-20 text-center">
			<p class="label">Laporan</p>
			<h1 class="mt-2 font-display text-2xl font-bold text-offwhite">Belum Ada Data</h1>
			<p class="mx-auto mt-3 max-w-sm text-sm text-muted">
				Upload video swing untuk mendapatkan laporan performa.
			</p>
			<a href="/analyze" class="btn-primary mt-8 inline-flex">Mulai Analisis</a>
		</div>
	{:else}
		<!-- Header -->
		<div class="mb-8 flex flex-col gap-4 border-b border-border pb-6 sm:flex-row sm:items-end sm:justify-between">
			<div>
				<p class="label">Laporan Sesi</p>
				<h1 class="page-title">Hasil Analisis</h1>
				<p class="mt-1 text-xs text-disabled">{formatDate(report.analyzed_at)}</p>
			</div>
			<a href="/analyze" class="btn-secondary shrink-0 text-xs">Sesi Baru</a>
		</div>

		<div class="grid gap-6 lg:grid-cols-12">
			<!-- Score -->
			<div class="card lg:col-span-4">
				<ScoreGauge score={report.score} />
			</div>

			<!-- Session meta -->
			<div class="card lg:col-span-8">
				<p class="label mb-4">Konfigurasi Sesi</p>
				<div class="grid gap-px border border-border bg-border sm:grid-cols-3">
					<div class="bg-graphite p-4">
						<p class="label">Club</p>
						<p class="font-display text-lg font-semibold text-offwhite">
							{CLUB_LABELS[report.club] ?? report.club}
						</p>
					</div>
					<div class="bg-graphite p-4">
						<p class="label">Pukulan</p>
						<p class="font-display text-lg font-semibold text-offwhite">
							{SHOT_LABELS[report.shot_type] ?? report.shot_type}
						</p>
					</div>
					<div class="bg-graphite p-4 sm:col-span-1">
						<p class="label">File</p>
						<p class="truncate text-sm text-muted">{report.filename}</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Metrics -->
		<div class="mt-6">
			<p class="label mb-3">Metrik Performa</p>
			<MetricsGrid metrics={report.metrics} />
		</div>

		<!-- Recommendation -->
		<div class="card mt-6">
			<p class="label">Rekomendasi</p>
			<p class="mt-2 text-sm leading-relaxed text-offwhite">{report.recommendation}</p>
		</div>

		<div class="mt-8 flex gap-3">
			<a href="/analyze" class="btn-primary">Analisis Lain</a>
			<a href="/" class="btn-secondary">Beranda</a>
		</div>
	{/if}
</section>
