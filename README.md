# Dragonfire & Christmas

A balanced Minecraft fantasy-adventure modpack built around **Book of Dragons**, with festive winter building, quality-of-life improvements, performance optimizations, and optional shaders.

## Target profile
- **Edition:** Minecraft Java
- **Minecraft:** 1.20.1
- **Mod loader:** Forge (47.x)
- **Java:** 17
- **Preferred launcher / distribution:** Modrinth App / Modrinth `.mrpack`

## Planned mod selection
### Core adventure
- [Book of Dragons](https://modrinth.com/mod/book-of-dragons) — dragon-focused adventure content.
- [AzureLib](https://modrinth.com/mod/azurelib) — animation library required by Book of Dragons.

### Christmas and winter
- [DecorationX: Christmas](https://modrinth.com/mod/decorationx-christmas) — festive decorative blocks and holiday atmosphere.
- [Gingerbread Houses](https://modrinth.com/project/gingerbread-houses) — gingerbread-themed structures and holiday content.
- [Snow! Real Magic!](https://modrinth.com/mod/snow-real-magic) — configurable snow accumulation and snow behavior.
- Snow! Real Magic! 10.7.0's Forge 1.20.1 listing does not identify Kiwi as a required dependency; the builder resolves dependencies from the selected file metadata.

### Building and decoration
- [Handcrafted](https://modrinth.com/mod/handcrafted) — furniture and interior decoration.
- [Chipped](https://modrinth.com/mod/chipped) — additional decorative block variants.
- [Athena](https://modrinth.com/mod/athena) and [Resourceful Lib](https://modrinth.com/mod/resourceful-lib) — libraries used by Chipped / related content.
- [Supplementaries](https://modrinth.com/mod/supplementaries) — vanilla-styled decorative and utility blocks.
- [Moonlight Lib](https://modrinth.com/mod/moonlight) — required by Supplementaries.

### Quality of life
- [Just Enough Items (JEI)](https://modrinth.com/mod/jei) — recipe and item browser.
- [Jade](https://modrinth.com/mod/jade) — information overlay for blocks and entities.

### Performance and shaders
- [Embeddium](https://modrinth.com/mod/embeddium) — Forge rendering optimization; use instead of Fabric Sodium.
- [Oculus](https://modrinth.com/mod/oculus) — Forge shader support, paired with Embeddium.
- [FerriteCore](https://modrinth.com/mod/ferrite-core) — memory optimization.
- [ModernFix](https://modrinth.com/mod/modernfix) — loading, memory, and bug fixes.
- [Entity Culling](https://modrinth.com/mod/entityculling) — client rendering optimization.

## Important compatibility notes
This is the **planned mod selection**, not yet a verified, import-ready `.mrpack`. A release pack must pin exact Modrinth version IDs that all target Forge 1.20.1, include every required dependency, and be launch-tested.
- Do not install Fabric Sodium in this Forge profile. Embeddium is the intended Forge alternative.
- Oculus is the shader loader for this Forge setup. Shader packs such as Complementary Reimagined or BSL are optional downloads and are not bundled here.
- Snow! Real Magic! 10.7.0 has a Forge 1.20.1 file; its listing does not require Kiwi.
- Book of Dragons requires a matching Forge 1.20.1 AzureLib dependency.
- Supplementaries requires Moonlight Lib.
- Chipped requires its matching library dependencies (including Athena and Resourceful Lib where specified by the selected file).
- Optional/client-only mods must not be copied to a dedicated server unless their project page says they are server-compatible.

## Build the importable Modrinth pack

A GitHub Actions workflow now builds the .mrpack from live Modrinth metadata, including exact file URLs, SHA-1/SHA-512 hashes, file sizes, and recursively resolved required dependencies.

1. Open the repository's **Actions** tab.
2. Select **Build Modrinth modpack**.
3. Choose **Run workflow** on the main branch if it has not already started automatically.
4. Open the completed run and download the **Dragonfire-and-Christmas-1.20.1-Forge** artifact.
5. Import the downloaded .mrpack into the Modrinth App.

The build fails rather than silently omitting a required dependency or choosing a non-Forge 1.20.1 file. The build report records the exact resolved versions.

## Build / testing checklist
- [ ] Resolve and pin exact Forge 1.20.1 Modrinth versions for every selected mod.
- [ ] Confirm each file's loader, game version, and dependency metadata.
- [ ] Generate the Modrinth `.mrpack` manifest with required dependencies.
- [ ] Launch-test a clean client profile.
- [ ] Test world creation and snow accumulation.
- [ ] Test Book of Dragons content and required libraries.
- [ ] Test Oculus with a supported shader pack.
- [ ] Test a dedicated server profile if multiplayer is desired.
- [ ] Publish the tested `.mrpack` as a GitHub release or attach it to the repository.

## Project status
The repository README and planning list are being organized. **The `.mrpack` is not yet built or tested**, so do not treat this repository state as a finished modpack release.