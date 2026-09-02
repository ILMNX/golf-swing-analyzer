import type { ClubType, ShotType, SwingAnalysis } from './types';

const API_BASE = '/api';

export async function uploadSwing(
	video: File,
	club: ClubType,
	shotType: ShotType
): Promise<SwingAnalysis> {
	const formData = new FormData();
	formData.append('video', video);
	formData.append('club', club);
	formData.append('shot_type', shotType);

	const response = await fetch(`${API_BASE}/upload-swing`, {
		method: 'POST',
		body: formData
	});

	const data = await response.json();

	if (!response.ok) {
		const message = data.error ?? 'Gagal menganalisis swing';
		throw new Error(message);
	}

	return data as SwingAnalysis;
}

export const REPORT_STORAGE_KEY = 'golf-swing-report';

export function saveReport(report: SwingAnalysis): void {
	sessionStorage.setItem(REPORT_STORAGE_KEY, JSON.stringify(report));
}

export function loadReport(): SwingAnalysis | null {
	const raw = sessionStorage.getItem(REPORT_STORAGE_KEY);
	if (!raw) return null;
	try {
		return JSON.parse(raw) as SwingAnalysis;
	} catch {
		return null;
	}
}

export function clearReport(): void {
	sessionStorage.removeItem(REPORT_STORAGE_KEY);
}

export function getAnnotatedVideoUrl(url?: string): string | null {
	if (!url) return null;
	if (url.startsWith('http')) return url;
	return url;
}
