const TUTORIAL_SEEN_KEY = 'swinglab_tutorial_seen';

export function hasSeenTutorial(): boolean {
	if (typeof localStorage === 'undefined') return false;
	return localStorage.getItem(TUTORIAL_SEEN_KEY) === '1';
}

export function markTutorialSeen(): void {
	if (typeof localStorage === 'undefined') return;
	localStorage.setItem(TUTORIAL_SEEN_KEY, '1');
}
