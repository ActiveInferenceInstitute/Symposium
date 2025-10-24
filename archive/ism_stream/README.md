# Archived ISM Stream Code

This directory contains the original ISM (Intelligent Soft Matter) Workshop code that has been archived during the v2.0 refactoring.

## Background

The original symposium package supported both:
1. **Active Inference Symposium** (AIF) - the primary focus going forward
2. **Intelligent Soft Matter Workshop** (ISM) - archived here for reference

## What Changed

In v2.0, the package was refactored to focus exclusively on the Active Inference Symposium. The ISM-specific code has been moved here to:
- Reduce complexity and focus
- Eliminate code duplication
- Streamline maintenance
- Improve clarity for AIF-specific workflows

## Contents

### Original ISM Files
- `1_Research_ISM_Presenters.py` - ISM presenter analysis
- `2_Research_ISM_Participants.py` - ISM participant profiling
- `3_ISM_Participant_FieldSHIFT.py` - Domain shifting analysis
- `4_ISM_Shifted_Catechisms.py` - ISM catechism generation
- `5_ISM_Collab_Catechisms.py` - ISM collaboration proposals
- `6_Visualize_ISM.py` - ISM-specific visualizations
- `Perplexity_Methods.py` - ISM-specific API methods (duplicate)
- `Visualization_Methods_ISM.py` - ISM visualizations (duplicate)
- `System_Prompts.json` - ISM prompts
- `outputs/` - ISM analysis results
- `Domain/` - ISM domain knowledge

### Why This Code Was Archived

1. **Focus**: The package now focuses on AIF Symposium exclusively
2. **Duplication**: Much of this code was duplicated in the main package
3. **Maintenance**: ISM-specific features are better maintained separately
4. **Clarity**: Clear separation between AIF and ISM workflows

## Migration Path

If you need ISM functionality:

1. **For reference**: Use this archived code as a starting point
2. **For active development**: Consider creating a separate ISM package
3. **For integration**: Adapt the core modules from the main package

## Restoration

To restore ISM functionality:

1. Copy relevant files back to the main directory
2. Update import paths and dependencies
3. Modify configuration to support both AIF and ISM
4. Update CLI to handle both workflows
5. Add tests for ISM-specific functionality

## Maintenance

This archive is preserved for:
- Historical reference
- Code reuse in future ISM projects
- Understanding the evolution of the package

**Note**: This code is not actively maintained and may not work with the current package structure.

## Contact

For questions about the ISM functionality or this archive:
- Check the main package documentation
- Review the refactoring implementation summary
- Contact the Active Inference Institute

---

*Archived during v2.0 refactoring (2025)*

