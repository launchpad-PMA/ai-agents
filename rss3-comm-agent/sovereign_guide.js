"use strict";

/**
 * Download order for a member's own machine.
 * The apps are free. The teaching is the order and the settings.
 * This catalog is the draft. It is not served from public/.
 */

const SOVEREIGN_GUIDE = {
  id: "sovereign-first-downloads",
  title: "Download these first",
  sections: [
    {
      id: "mint",
      kind: "app",
      order: 1,
      title: "Linux Mint",
      free: true,
      url: "https://linuxmint.com",
      when: "new-pc",
    },
    {
      id: "ollama",
      kind: "app",
      order: 2,
      title: "Ollama",
      free: true,
      url: "https://ollama.com/download",
      when: "every-machine",
    },
    {
      id: "models",
      kind: "teaching",
      order: 3,
      title: "Three models",
      models: ["qwen3.6:27b", "qwen3.8:27b", "nomic-embed-text"],
      temperature: 0.3,
      context: 64000,
    },
    {
      id: "obsidian",
      kind: "app",
      order: 4,
      title: "Obsidian",
      free: true,
      url: "https://obsidian.md",
      when: "after-models",
    },
    {
      id: "stay-home",
      kind: "teaching",
      order: 5,
      title: "Notes stay home",
      rules: ["sync off", "vault on this computer", "not the church archive"],
    },
  ],
};

module.exports = { SOVEREIGN_GUIDE };
