# Azure Void Image Style — Codex Skill

A reusable Codex image-art-direction skill for luminous electric-blue + white visuals with aquatic glow, editorial composition, and modern Japanese game-UI energy.

## Install

Place this folder in your Codex skills directory. Current Codex skills use a directory containing `SKILL.md`; Codex can then discover the skill by its `name` and `description` metadata.

Recommended folder name:

```text
azure-void-image-style/
  SKILL.md
  references/
    style-guide.md
```

In Codex, you can invoke it explicitly with:

```text
$azure-void-image-style Create a 16:9 thumbnail about abstract thinking. Huge blue title, grayscale subject, white background, glowing blue fluid trail.
```

The skill will use `$imagegen` when image generation is available.

## Example prompts

```text
$azure-void-image-style Make an Instagram cover about deep work. A lone person at a desk, mostly grayscale, bright white environment, glowing azure ribbon spiraling toward the desk, no text.
```

```text
$azure-void-image-style Create a 16:9 YouTube thumbnail for "FIRST PRINCIPLES". Giant elegant blue type, sparse white background, central grayscale thinker, luminous watery blue reflection on the floor.
```
