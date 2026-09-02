<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onDestroy, onMount } from 'svelte';
	import { Info, Loader2, Upload } from 'lucide';
	import AnalysisProgress from '$lib/components/AnalysisProgress.svelte';
	import ClubSelector from '$lib/components/ClubSelector.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import TutorialModal from '$lib/components/TutorialModal.svelte';
	import { uploadSwing, saveReport } from '$lib/api';
	import { hasSeenTutorial, markTutorialSeen } from '$lib/tutorialStorage';
	import type { ClubType, ShotType } from '$lib/types';
	import { ANALYSIS_STAGES, SHOT_OPTIONS } from '$lib/types';

	let club = $state<ClubType>('iron_7');
	let shotType = $state<ShotType>('full_swing');
	let videoFile = $state<File | null>(null);
	let videoPreview = $state<string | null>(null);
	let showTutorial = $state(false);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let dragOver = $state(false);
	let stageIndex = $state(0);
	let stageTimer: ReturnType<typeof setInterval> | null = null;

	const maxSizeMB = 100;

	const VALID_CLUBS = new Set([
		'driver', 'wood_3', 'wood_5', 'iron_3', 'iron_5', 'iron_7', 'iron_9', 'wedge', 'putter'
	]);
	const VALID_SHOTS = new Set(['full_swing', 'chip', 'pitch', 'putt']);

	onMount(() => {
		const clubParam = page.url.searchParams.get('club');
		const shotParam = page.url.searchParams.get('shot_type');
		if (clubParam && VALID_CLUBS.has(clubParam)) club = clubParam as ClubType;
		if (shotParam && VALID_SHOTS.has(shotParam)) shotType = shotParam as ShotType;
		if (!hasSeenTutorial()) showTutorial = true;
	});

	function closeTutorial() {
		showTutorial = false;
		markTutorialSeen();
	}

	function startStageTimer() {
		stageIndex = 0;
		stageTimer = setInterval(() => {
			stageIndex = Math.min(stageIndex + 1, ANALYSIS_STAGES.length - 1);
		}, 3500);
	}

	function stopStageTimer() {
		if (stageTimer) {
			clearInterval(stageTimer);
			stageTimer = null;
		}
	}

	onDestroy(stopStageTimer);

	function handleFileSelect(file: File | undefined) {
		error = null;
		if (!file) return;

		if (!file.type.startsWith('video/')) {
			error = 'File harus berupa video (MP4, MOV, AVI, dll.)';
			return;
		}

		if (file.size > maxSizeMB * 1024 * 1024) {
			error = `Ukuran file maksimal ${maxSizeMB} MB`;
			return;
		}

		if (videoPreview) URL.revokeObjectURL(videoPreview);
		videoFile = file;
		videoPreview = URL.createObjectURL(file);
	}

	function onFileInput(e: Event) {
		const input = e.target as HTMLInputElement;
		handleFileSelect(input.files?.[0]);
	}

	function onDrop(e: DragEvent) {
		e.preventDefault();
		dragOver = false;
		handleFileSelect(e.dataTransfer?.files?.[0]);
	}

	function removeVideo() {
		if (videoPreview) URL.revokeObjectURL(videoPreview);
		videoFile = null;
		videoPreview = null;
	}

	async function submit() {
		if (!videoFile) {
			error = 'Upload video swing terlebih dahulu';
			return;
		}

		loading = true;
		error = null;
		startStageTimer();

		try {
			const result = await uploadSwing(videoFile, club, shotType);
			saveReport(result);
			await goto('/report');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Terjadi kesalahan';
		} finally {
			stopStageTimer();
			loading = false;
		}
	}
</script>

<section class="relative overflow-hidden border-b border-border">
	<div class="pointer-events-none absolute inset-0" aria-hidden="true">
		<img
			src="/analyze/driving-range-bay.jpeg"
			alt=""
			class="absolute inset-0 h-full w-full object-cover object-[55%_center] sm:object-[60%_center]"
		/>
		<div class="absolute inset-0 bg-obsidian/45"></div>
		<div
			class="absolute inset-0 bg-gradient-to-r from-obsidian from-0% via-obsidian/80 via-45% to-obsidian/25 to-100%"
		></div>
		<div class="absolute inset-0 bg-gradient-to-b from-obsidian/50 via-transparent to-obsidian/55"></div>
	</div>

	<div class="container-page relative z-10 py-8 sm:py-10">
	<div class="mb-6 flex flex-col gap-4 sm:mb-8 sm:flex-row sm:items-end sm:justify-between">
		<div class="min-w-0">
			<p class="label">Sesi Baru</p>
			<h1 class="page-title">Analisis Swing</h1>
		</div>
		<button type="button" class="btn-secondary shrink-0 self-start text-xs sm:self-auto" onclick={() => (showTutorial = true)}>
			<Icon icon={Info} size={15} />
			Panduan Rekaman
		</button>
	</div>

	<form
		class="flex w-full min-w-0 flex-col gap-5"
		onsubmit={(e) => {
			e.preventDefault();
			submit();
		}}
	>
		<div class="card w-full">
			<p class="label">Jenis Pukulan</p>
			<div class="grid grid-cols-4 gap-1.5 sm:gap-2">
				{#each SHOT_OPTIONS as shot}
					<button
						type="button"
						title={shot.description}
						class="min-w-0 rounded-md border px-1 py-2.5 text-center transition sm:px-2 sm:py-3
							{shotType === shot.value
							? 'border-golf bg-golf/10 text-offwhite'
							: 'border-border text-muted hover:border-muted hover:text-offwhite'}"
						onclick={() => (shotType = shot.value)}
					>
						<span class="block text-[10px] font-semibold uppercase leading-tight tracking-wide sm:text-xs">
							{shot.label}
						</span>
					</button>
				{/each}
			</div>
		</div>

		<div class="grid w-full min-w-0 gap-5 lg:grid-cols-12">
			<div class="min-w-0 lg:col-span-4">
				<div class="card">
					<p class="label">Club</p>
					<ClubSelector bind:value={club} />
				</div>
			</div>

			<div class="min-w-0 lg:col-span-8">
				<div class="card h-full">
					<p class="label">Video Swing</p>

					{#if videoPreview}
						<div class="relative w-full overflow-hidden border border-border bg-obsidian">
							<video src={videoPreview} controls class="max-h-72 w-full object-contain sm:max-h-80">
								<track kind="captions" />
							</video>
							<button
								type="button"
								class="absolute right-2 top-2 border border-border bg-graphite px-2 py-1 text-xs text-muted hover:text-offwhite"
								onclick={removeVideo}
							>
								Hapus
							</button>
						</div>
						<p class="mt-2 truncate text-xs text-disabled">{videoFile?.name}</p>
					{:else}
						<div
							class="flex min-h-48 w-full cursor-pointer flex-col items-center justify-center border border-dashed px-4 py-12 transition sm:min-h-64 sm:px-6 sm:py-16
								{dragOver ? 'border-golf bg-golf/5' : 'border-border hover:border-muted'}"
							role="button"
							tabindex="0"
							ondragover={(e) => {
								e.preventDefault();
								dragOver = true;
							}}
							ondragleave={() => (dragOver = false)}
							ondrop={onDrop}
							onclick={() => document.getElementById('video-upload')?.click()}
							onkeydown={(e) => e.key === 'Enter' && document.getElementById('video-upload')?.click()}
						>
							<Icon icon={Upload} size={28} class="mb-3 text-muted" />
							<p class="text-center text-sm font-medium text-offwhite">Seret video ke sini</p>
							<p class="mt-1 text-center text-xs text-muted">
								atau klik untuk memilih &middot; maks. {maxSizeMB} MB
							</p>
						</div>
					{/if}

					<input
						id="video-upload"
						type="file"
						accept="video/*"
						class="hidden"
						onchange={onFileInput}
					/>

					{#if error}
						<p class="mt-4 border border-error/30 bg-error/5 px-3 py-2 text-sm text-error">
							{error}
						</p>
					{/if}

					<div class="mt-5 flex justify-end border-t border-border pt-4 sm:mt-6 sm:pt-5">
						<button type="submit" class="btn-primary w-full sm:w-auto" disabled={loading || !videoFile}>
							{#if loading}
								<Icon icon={Loader2} size={16} class="animate-spin" />
								Memproses...
							{:else}
								Analisis Swing
							{/if}
						</button>
					</div>
				</div>
			</div>
		</div>
	</form>
	</div>
</section>

{#if loading}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-obsidian/90 p-4">
		<AnalysisProgress activeIndex={stageIndex} {club} {shotType} />
	</div>
{/if}

<TutorialModal open={showTutorial} onclose={closeTutorial} />
