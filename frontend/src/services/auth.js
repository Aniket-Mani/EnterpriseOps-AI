const PROFILE_KEY = "eo.profile";

export function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem(PROFILE_KEY)) || {
      name: "Aniket Mani",
      role: "Workspace admin",
      initials: "AM",
    };
  } catch {
    return { name: "Aniket Mani", role: "Workspace admin", initials: "AM" };
  }
}

export function saveCurrentUser(profile) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
  return profile;
}

export function clearCurrentUser() {
  localStorage.removeItem(PROFILE_KEY);
}
