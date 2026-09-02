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

<section class="container-page py-8 sm:py-10">
	{#if !report}
		<div class="w-full border border-border bg-graphite px-4 py-16 text-center sm:px-6 sm:py-20">
			<p class="label">Laporan</p>
			<h1 class="mt-2 font-display text-xl font-bold text-offwhite sm:text-2xl">Belum Ada Data</h1>
			<p class="mx-auto mt-3 max-w-sm text-sm text-muted">
				Upload video swing untuk mendapatkan laporan performa.
			</p>
			<a href="/analyze" class="btn-primary mt-8 inline-flex">Mulai Analisis</a>
		</div>
	{:else}
		<div class="mb-6 flex flex-col gap-4 border-b border-border pb-6 sm:mb-8 sm:flex-row sm:items-end sm:justify-between">
			<div class="min-w-0">
				<p class="label">Laporan Sesi</p>
				<h1 class="page-title">Hasil Analisis</h1>
				<p class="mt-1 text-xs text-disabled">{formatDate(report.analyzed_at)}</p>
			</div>
			<a href="/analyze" class="btn-secondary w-full shrink-0 text-xs sm:w-auto">Sesi Baru</a>
		</div>

		<div class="grid w-full min-w-0 gap-5 sm:gap-6 lg:grid-cols-12">
			<div class="card min-w-0 lg:col-span-4">
				<ScoreGauge score={report.score} />
			</div>

			<div class="card min-w-0 lg:col-span-8">
				<p class="label mb-4">Konfigurasi Sesi</p>
				<div class="grid w-full min-w-0 gap-px border border-border bg-border sm:grid-cols-3">
					<div class="min-w-0 bg-graphite p-4">
						<p class="label">Club</p>
						<p class="font-display text-base font-semibold text-offwhite sm:text-lg">
							{CLUB_LABELS[report.club] ?? report.club}
						</p>
					</div>
					<div class="min-w-0 bg-graphite p-4">
						<p class="label">Pukulan</p>
						<p class="font-display text-base font-semibold text-offwhite sm:text-lg">
							{SHOT_LABELS[report.shot_type] ?? report.shot_type}
						</p>
					</div>
					<div class="min-w-0 bg-graphite p-4 sm:col-span-1">
						<p class="label">File</p>
						<p class="truncate text-sm text-muted">{report.filename}</p>
					</div>
				</div>
			</div>
		</div>

		<div class="mt-5 w-full min-w-0 sm:mt-6">
			<p class="label mb-3">Metrik Performa</p>
			<MetricsGrid metrics={report.metrics} />
		</div>

		<div class="card mt-5 w-full min-w-0 sm:mt-6">
			<p class="label">Rekomendasi</p>
			<p class="mt-2 text-sm leading-relaxed text-offwhite">{report.recommendation}</p>
		</div>

		<div class="mt-6 flex w-full flex-col gap-3 sm:mt-8 sm:flex-row">
			<a href="/analyze" class="btn-primary w-full sm:w-auto">Analisis Lain</a>
			<a href="/" class="btn-secondary w-full sm:w-auto">Beranda</a>
		</div>
	{/if}
</section>
