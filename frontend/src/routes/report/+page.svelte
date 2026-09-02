<script lang="ts">
	import { onMount } from 'svelte';
	import DetailedMetrics from '$lib/components/DetailedMetrics.svelte';
	import NextSwingFocus from '$lib/components/NextSwingFocus.svelte';
	import SpiderChart from '$lib/components/SpiderChart.svelte';
	import { getAnnotatedVideoUrl, loadReport } from '$lib/api';
	import type { SwingAnalysis } from '$lib/types';
	import { CLUB_LABELS, SHOT_LABELS } from '$lib/types';

	let report = $state<SwingAnalysis | null>(null);
	let videoError = $state(false);
	let videoRetry = $state(0);

	const videoUrl = $derived(
		report?.annotated_video_url ? getAnnotatedVideoUrl(report.annotated_video_url) : null
	);

	onMount(() => {
		report = loadReport();
	});

	$effect(() => {
		if (videoUrl) {
			videoError = false;
		}
	});

	function retryVideo() {
		videoError = false;
		videoRetry += 1;
	}

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
		<!-- Header -->
		<div class="mb-6 flex flex-col gap-4 border-b border-border pb-6 sm:mb-8 sm:flex-row sm:items-end sm:justify-between">
			<div class="min-w-0">
				<p class="label">Laporan Sesi</p>
				<h1 class="page-title">Hasil Analisis</h1>
				<p class="mt-1 text-xs text-disabled">{formatDate(report.analyzed_at)}</p>
			</div>
			<div class="flex flex-wrap items-center gap-3 text-xs text-muted">
				<span>{CLUB_LABELS[report.club] ?? report.club}</span>
				<span class="text-border">|</span>
				<span>{SHOT_LABELS[report.shot_type] ?? report.shot_type}</span>
				{#if report.tuning?.profile_id}
					<span class="text-border">|</span>
					<span class="text-disabled" title="Tuning profile">Profile: {report.tuning.profile_id}</span>
				{/if}
				<span class="text-border">|</span>
				<span class="truncate">{report.filename}</span>
			</div>
		</div>

		<!-- Main analysis: Spider chart + score -->
		<div class="card mb-5 w-full min-w-0 sm:mb-6">
			<p class="label mb-6">Analisis Utama</p>
			<div class="grid w-full min-w-0 items-center gap-8 lg:grid-cols-2">
				<div class="flex justify-center">
					<SpiderChart summary={report.metrics.summary} size={320} />
				</div>
				<div class="flex flex-col items-center justify-center gap-4 border-t border-border pt-6 lg:border-l lg:border-t-0 lg:pl-8 lg:pt-0">
					<div class="text-center">
						<p class="label">Overall Score</p>
						<p class="font-display text-6xl font-bold tabular-nums text-offwhite">{report.score}</p>
						<p class="mt-1 text-sm text-muted">dari 100</p>
					</div>
					<div class="grid w-full max-w-xs grid-cols-2 gap-2 text-center text-xs sm:max-w-sm sm:grid-cols-3">
						{#each [
							{ label: 'Tempo', value: report.metrics.summary.tempo },
							{ label: 'Postur', value: report.metrics.summary.posture },
							{ label: 'Rotasi', value: report.metrics.summary.rotation },
							{ label: 'Balance', value: report.metrics.summary.balance },
							{ label: 'Kepala', value: report.metrics.summary.head_stability }
						] as item}
							<div class="border border-border bg-obsidian px-2 py-2">
								<p class="text-muted">{item.label}</p>
								<p class="font-display font-semibold text-offwhite">{item.value}</p>
							</div>
						{/each}
					</div>
				</div>
			</div>
		</div>

		<!-- Notes / Recommendation -->
		<div class="card mb-5 w-full min-w-0 sm:mb-6">
			<p class="label">Catatan Analisis</p>
			<p class="mt-3 text-sm leading-relaxed text-offwhite">{report.recommendation}</p>
			{#if report.validation}
				<div class="mt-4 border-t border-border pt-4">
					<p class="label mb-2">Kualitas Video</p>
					<div class="flex flex-wrap gap-4 text-xs text-muted">
						<span>Ketajaman: {report.validation.sharpness.toFixed(0)}</span>
						<span>Visibilitas sendi: {(report.validation.visible_keypoint_ratio * 100).toFixed(0)}%</span>
						<span>{report.validation.video.fps.toFixed(0)} fps</span>
						<span>{report.validation.video.duration_sec}s &middot; {report.validation.video.frame_count} frame</span>
						<span>{report.metrics.frames_analyzed} frame dianalisis</span>
					</div>
					{#if report.metrics.quality?.low_fps_warning}
						<p class="mt-2 text-xs text-muted">
							Video di bawah 45 fps — metrik tempo dan rotasi kurang akurat. Rekam ulang di 60 fps untuk hasil lebih baik.
						</p>
					{/if}
				</div>
			{/if}
			{#if report.trim?.applied}
				<div class="mt-4 border-t border-border pt-4">
					<p class="label mb-2">Auto-Trim Segmen Swing</p>
					<p class="text-sm text-offwhite">
						Setup <span class="font-semibold text-highlight">{report.trim.setup_trimmed_sec.toFixed(1)}s</span>
						dihapus &middot; menganalisis
						<span class="font-semibold">{report.trim.trimmed_start_sec.toFixed(1)}s – {report.trim.trimmed_end_sec.toFixed(1)}s</span>
						dari {report.trim.original_duration_sec.toFixed(1)}s total
					</p>
					<p class="mt-2 text-xs text-muted">
						Frame sumber: {report.trim.source_start_frame}–{report.trim.source_end_frame}
						&middot; Address #{report.trim.address_frame_source}
						&middot; Top #{report.trim.top_frame_source}
						&middot; Impact #{report.trim.impact_frame_source}
					</p>
					<p class="mt-1 text-xs text-disabled">
						Video tracking hanya menampilkan segmen yang dipotong — bukan full upload.
					</p>
				</div>
			{/if}
		</div>

		<!-- Next swing focus -->
		<NextSwingFocus {report} />

		<!-- Annotated video -->
		{#if videoUrl}
			<div class="card mb-5 w-full min-w-0 sm:mb-6">
				<p class="label">Video Tracking Sendi</p>
				<div class="overflow-hidden border border-border bg-obsidian">
					{#if videoError}
						<div class="flex min-h-48 flex-col items-center justify-center gap-3 p-6 text-center text-sm text-muted">
							<p>Video tidak dapat diputar. Pastikan layanan backend masih berjalan, lalu coba lagi.</p>
							<div class="flex flex-wrap justify-center gap-2">
								<button type="button" class="btn-secondary text-xs" onclick={retryVideo}>
									Coba putar lagi
								</button>
								<a href={videoUrl} class="btn-secondary text-xs" target="_blank" rel="noopener">
									Buka video langsung
								</a>
							</div>
						</div>
					{:else}
						{#key `${videoUrl}-${videoRetry}`}
							<video
								src={videoUrl}
								controls
								playsinline
								preload="metadata"
								class="max-h-[32rem] w-full object-contain"
								onerror={() => (videoError = true)}
							></video>
						{/key}
					{/if}
				</div>
				<p class="mt-2 text-xs text-muted">
					Hijau = skeleton &middot; titik terang = sendi &middot; garis putih = jejak gerakan
				</p>
			</div>
		{/if}

		<!-- Detailed metrics -->
		<div class="w-full min-w-0">
			<p class="label mb-3">Metrik Detail</p>
			<DetailedMetrics metrics={report.metrics} />
		</div>

		<div class="mt-6 flex w-full flex-col gap-3 sm:mt-8 sm:flex-row">
			<a
				href="/analyze?club={report.club}&shot_type={report.shot_type}"
				class="btn-primary w-full sm:w-auto"
			>
				Pukulan Berikutnya ({CLUB_LABELS[report.club] ?? report.club})
			</a>
			<a href="/analyze" class="btn-secondary w-full sm:w-auto">Analisis Lain</a>
			<a href="/" class="btn-secondary w-full sm:w-auto">Beranda</a>
		</div>
	{/if}
</section>
