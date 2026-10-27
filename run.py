#!/usr/bin/env python3
"""
Symposium Interactive Runner

Main interactive interface for the Symposium package for the selected Active Inference Symposium edition.
Optimized for UV package manager.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

from symposium.core.config import Config
from symposium.core.edition import Edition

logger = logging.getLogger(__name__)
current_dir = Path(__file__).resolve().parent


class SymposiumRunner:
    """Interactive runner for Symposium operations for selectable symposium editions."""

    def __init__(self, year=None, config_file=None):
        """Select one edition without creating directories or contacting providers."""
        implicit_config = Path("config.json")
        selected_config = (
            Path(config_file)
            if config_file is not None
            else (implicit_config if implicit_config.exists() else None)
        )
        self.configuration = Config(config_file=selected_config)
        self.config = self.configuration.to_dict()
        self.data_dir = self.configuration.get_path("data_dir")
        self.outputs_dir = self.configuration.get_path("outputs_dir")
        self.edition = Edition(
            year=self.configuration.get("edition.year") if year is None else year,
            data_dir=self.data_dir,
            outputs_dir=self.outputs_dir,
        )

    def load_config(self) -> Dict[str, Any]:
        """Return the shared configuration used by the CLI and runner."""
        return self.configuration.to_dict()

    def create_api_client(self, provider):
        """Apply configured credentials and model parameters consistently."""
        from symposium.core.api import APIClient

        options = dict(self.configuration.get_api_config(provider))
        options.pop("api_key", None)
        return APIClient.create(
            provider, api_key=self.configuration.get_api_key(provider), **options
        )

    def display_header(self):
        """Display the main header."""
        logger.info("Displaying header")
        print("╔════════════════════════════════════════════════════════════════╗")
        print(f"║         🎯 SYMPOSIUM {self.edition.year} - ACTIVE INFERENCE 🎯                ║")
        print("║             Participant Analysis & Research Tool               ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print()

    def display_menu(self):
        """Display the main menu options."""
        logger.info("Displaying menu options")
        print("📋 AVAILABLE OPERATIONS:")
        print("─" * 50)
        print("1.  📊 List Available Data")
        print(f"2.  🎯 Analyze {self.edition.year} Participants (Complete Analysis)")
        print("3.  📊 Generate Column Summaries & Word Clouds")
        print("4.  🔍 Background Research (Single Participant)")
        print("5.  📚 Personalized Curriculum (Single Participant)")
        print("6.  🌐 Create Visualizations")
        print("7.  🔧 Configuration Management")
        print("8.  🧪 Test System Components")
        print("9.  🚪 Exit")
        print()

    def get_choice(self) -> str:
        """Get user choice with validation."""
        while True:
            try:
                choice = input("Enter your choice (1-9): ").strip()
                if choice in [str(i) for i in range(1, 10)]:
                    return choice
                else:
                    print("❌ Please enter a number between 1 and 9.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                sys.exit(0)

    def list_available_data(self):
        """List available data in the data directory."""
        print("📊 AVAILABLE DATA")
        print("=" * 50)

        # Check selected-edition participant data (primary focus)
        participants_csv = self.edition.participants_csv
        if participants_csv.exists():
            import pandas as pd

            try:
                df = pd.read_csv(participants_csv)
                print(
                    f"\n🎯 {self.edition.year} ACTIVE INFERENCE SYMPOSIUM PARTICIPANTS: {len(df)} total"
                )

                from symposium.core.data_loader import DataLoader

                public_count = len(DataLoader.load_participant_data(participants_csv))
                print(f"   ✅ Public sharing: {public_count} participants")
                print(f"   📊 Data fields: {len(df.columns)}")
                print("   💡 Use Option 2 for complete analysis")
            except Exception as e:
                print(f"\n🎯 {self.edition.year} PARTICIPANT DATA: Error reading CSV: {e}")
        else:
            print(f"\n⚠️  {self.edition.year} participant data not found")
            print(f"   Expected location: {participants_csv}")

        print()

    def analyze_participants(self):
        """Analyze selected-edition Symposium participants with complete analysis."""
        logger.info(f"Starting {self.edition.year} symposium participants analysis")
        print(f"🎯 {self.edition.year} SYMPOSIUM PARTICIPANTS (COMPLETE ANALYSIS)")
        print("=" * 60)

        # Check participant data
        participants_csv = self.edition.participants_csv
        if not participants_csv.exists():
            logger.error(f"{self.edition.year} Participant data not found: {participants_csv}")
            print(f"❌ {self.edition.year} Participant data not found: {participants_csv}")
            print(f"   Expected location: {participants_csv}")
            return

        print(f"📁 Found {self.edition.year} participant data: {participants_csv}")
        logger.info(f"Found {self.edition.year} participant data: {participants_csv}")

        # Load and count participants
        try:
            import pandas as pd

            df = pd.read_csv(participants_csv)
            total_participants = len(df)
            print(f"📊 Total participants in CSV: {total_participants}")

            from symposium.core.data_loader import DataLoader

            public_count = len(DataLoader.load_participant_data(participants_csv))
            print(f"👥 Participants agreeing to share publicly: {public_count}")
            if not public_count:
                print(
                    "No eligible participants yet. Populate and validate this edition before analysis."
                )
                return

        except Exception as e:
            logger.error(f"Error reading participant CSV: {e}")
            print(f"❌ Error reading participant data: {e}")
            return

        # Check API keys
        has_perplexity = bool(self.configuration.get_api_key("perplexity"))
        has_openrouter = bool(self.configuration.get_api_key("openrouter"))

        print("\n🔑 API KEYS:")
        print(
            f"   Perplexity (Background Research): {'✅ Available' if has_perplexity else '❌ Missing'}"
        )
        print(
            f"   OpenRouter (Curricula & Analysis): {'✅ Available' if has_openrouter else '❌ Missing'}"
        )

        if not (has_perplexity or has_openrouter):
            print("\n❌ At least one API key is required")
            print("   Set PERPLEXITY_API_KEY or OPENROUTER_API_KEY in .env file")
            return

        # Analysis options
        print("\n🎯 ANALYSIS OPTIONS:")
        print("1. 📋 Profile Analysis Only")
        print("2. 🔍 Background Research Only (Perplexity)")
        print("3. 📚 Personalized Curricula Only (OpenRouter)")
        print("4. 🎯 Complete Analysis (All Features)")

        while True:
            choice = input("Choose analysis type (1-4): ").strip()
            try:
                analysis_type = int(choice)
                if 1 <= analysis_type <= 4:
                    break
                else:
                    print("❌ Please choose between 1 and 4")
            except ValueError:
                print("❌ Please enter a number")

        # Set options based on choice
        include_background = analysis_type in [2, 4]
        include_curriculum = analysis_type in [3, 4]
        include_analysis = analysis_type in [1, 4]

        # Check if required APIs are available
        if include_background and not has_perplexity:
            print("❌ Background research requires Perplexity API key")
            return
        if (include_analysis or include_curriculum) and not has_openrouter:
            print("❌ Profile analysis and curricula require OpenRouter API key")
            return

        print(f"\n🔄 Starting {self.edition.year} Symposium participant analysis...")
        logger.info(
            f"Starting {self.edition.year} symposium analysis with options: background={include_background}, curriculum={include_curriculum}"
        )

        try:
            # Import modules
            import time

            overall_start = time.time()

            logger.info(
                f"Importing symposium modules for {self.edition.year} participant processing"
            )
            from symposium.analysis.participants import ParticipantAnalyzer

            logger.debug("Modules imported successfully")

            # Create output directory structure
            output_base = self.edition.output_dir / "people"
            output_base.mkdir(parents=True, exist_ok=True)
            logger.info(f"Output directory: {output_base}")

            # Create appropriate API clients based on selected features
            # Background research ALWAYS uses Perplexity (Sonar model)
            # Profile analysis and curriculum use OpenRouter (Claude)
            perplexity_client = None
            openrouter_client = None

            if include_background:
                logger.debug("Creating Perplexity API client (Sonar model) for background research")
                perplexity_client = self.create_api_client("perplexity")
                print("   🔍 Using Perplexity Sonar for background research")

            if include_analysis or include_curriculum:
                logger.debug("Creating OpenRouter API client (Claude) for analysis and curricula")
                openrouter_client = self.create_api_client("openrouter")
                print("   🤖 Using OpenRouter Claude for analysis and curricula")

            # Use OpenRouter as primary client for analyzer (it does profile analysis)
            primary_client = openrouter_client if openrouter_client else perplexity_client
            analyzer = ParticipantAnalyzer(primary_client, self.config.get("data", {}))
            logger.debug("Participant analyzer created")

            # Run analysis with appropriate clients
            results = analyzer.analyze_all_participants(
                participants_csv,
                output_base,
                include_background_research=include_background,
                include_curriculum=include_curriculum,
                perplexity_client=perplexity_client,
                include_profile=include_analysis,
            )

            if len(results) != public_count or any(
                "error" in result for result in results.values()
            ):
                print(
                    "❌ Processing incomplete. Completed reports were preserved; inspect the errors above."
                )
                return

            overall_time = time.time() - overall_start
            logger.info(
                f"{self.edition.year} Participant processing completed: {len(results)} participants in {overall_time:.1f}s"
            )
            print(f"✅ {self.edition.year} Participant processing completed!")
            print(f"📁 Results saved to: {output_base}/")
            print(f"📊 Processed {len(results)} participants in {overall_time:.1f}s")

            # Show results summary
            print("\n📋 ANALYSIS SUMMARY:")
            print(f"   • Profile Analysis: {'✅' if include_analysis else '❌'}")
            print(f"   • Background Research: {'✅' if include_background else '❌'}")
            print(f"   • Personalized Curricula: {'✅' if include_curriculum else '❌'}")

            print(f"\n📁 Output location: {output_base}/")
            print("   Individual participant reports in subdirectories")

        except ImportError as e:
            logger.error(f"Import error: {e}", exc_info=True)
            print(f"❌ Module import failed: {e}")
            print("   Run the setup script: ./symposium.sh")
            print("   Or manually: uv pip install -e .")
        except Exception as e:
            logger.error(f"{self.edition.year} Participant processing failed: {e}", exc_info=True)
            print(f"❌ Processing failed: {e}")
            print("   Check your API keys and network connection.")

        print()

    def analyze_2025_participants(self):
        """Compatibility alias; operates on the explicitly selected edition."""
        return self.analyze_participants()

    def generate_column_summaries(self):
        """Generate column summaries and word clouds."""
        logger.info("Starting column summary generation")
        print("📊 GENERATE COLUMN SUMMARIES & WORD CLOUDS")
        print("=" * 60)

        # Check participant data
        participants_csv = self.edition.participants_csv
        if not participants_csv.exists():
            logger.error(f"{self.edition.year} Participant data not found: {participants_csv}")
            print(f"❌ {self.edition.year} Participant data not found: {participants_csv}")
            return

        print(f"📁 Found {self.edition.year} participant data: {participants_csv}")

        # Check API key
        has_openrouter = bool(self.configuration.get_api_key("openrouter"))
        if not has_openrouter:
            print("❌ OpenRouter API key required for LLM-based summaries")
            print("   Set OPENROUTER_API_KEY in .env file")
            return

        print("🔄 Generating column summaries...")

        try:
            from symposium.analysis.participants import ParticipantAnalyzer

            client = self.create_api_client("openrouter")
            analyzer = ParticipantAnalyzer(client, self.config.get("data", {}))

            output_base = self.edition.output_dir / "column_summaries"
            output_base.mkdir(parents=True, exist_ok=True)

            column_summaries = analyzer.generate_column_summaries(participants_csv, output_base)

            print(f"✅ Generated summaries for {len(column_summaries)} columns")
            print(f"📁 Column summaries saved to: {output_base}/")

        except Exception as e:
            logger.error(f"Column summary generation failed: {e}")
            print(f"❌ Column summary generation failed: {e}")

        print()

    def research_single_participant(self):
        """Research background for a single participant."""
        logger.info("Starting single participant background research")
        print("🔍 BACKGROUND RESEARCH (SINGLE PARTICIPANT)")
        print("=" * 60)

        # Check API key
        if not self.configuration.get_api_key("perplexity"):
            print("❌ Perplexity API key required for background research")
            print("   Set PERPLEXITY_API_KEY in .env file")
            return

        # Check participant data
        participants_csv = self.edition.participants_csv
        if not participants_csv.exists():
            print(f"❌ {self.edition.year} Participant data not found: {participants_csv}")
            return

        try:
            from symposium.analysis.participants import ParticipantAnalyzer
            from symposium.core.data_loader import DataLoader

            # Load participant data
            participants = DataLoader.load_participant_data(participants_csv)

            # Show available participants
            print(f"\n📊 Available participants ({len(participants)} total):")
            for i, name in enumerate(sorted(participants.keys())[:10], 1):
                print(f"   {i}. {name}")
            if len(participants) > 10:
                print(f"   ... and {len(participants) - 10} more")

            # Get participant name
            participant_name = input("\nEnter participant name (or partial match): ").strip()

            # Find matching participants
            matches = [
                name for name in participants.keys() if participant_name.lower() in name.lower()
            ]

            if not matches:
                print(f"❌ No participant found matching: {participant_name}")
                return
            elif len(matches) > 1:
                print("\n📋 Multiple matches found:")
                for i, name in enumerate(matches, 1):
                    print(f"   {i}. {name}")
                try:
                    choice = int(input("Choose participant (number): ").strip()) - 1
                except ValueError:
                    print("❌ Invalid number entered.")
                    return
                if not 0 <= choice < len(matches):
                    print("❌ Selection out of range.")
                    return
                participant_name = matches[choice]
            else:
                participant_name = matches[0]

            print(f"\n🔍 Researching {participant_name}...")

            # Create Perplexity API client (Sonar model for background research)
            logger.info(f"Creating Perplexity API client (Sonar model) for {participant_name}")
            client = self.create_api_client("perplexity")
            analyzer = ParticipantAnalyzer(client, self.config.get("data", {}))
            print("   🔍 Using Perplexity Sonar for research")

            # Research participant
            participant_data = participants[participant_name]
            background = analyzer.research_participant_background(participant_data)

            # Save result
            output_base = self.edition.output_dir / "single_research"
            output_base.mkdir(parents=True, exist_ok=True)

            from symposium.io.writers import ReportWriter

            ReportWriter.save_participant_report(
                participant_name, background, output_base, "background_research"
            )

            print("✅ Background research completed!")
            print(f"📁 Results saved to: {output_base}/{participant_name}/")
            print("\n📄 Preview (first 300 chars):")
            print(f"   {(background or '')[:300]}...")

        except Exception as e:
            logger.error(f"Background research failed: {e}")
            print(f"❌ Background research failed: {e}")

        print()

    def generate_single_curriculum(self):
        """Generate personalized curriculum for a single participant."""
        logger.info("Starting single participant curriculum generation")
        print("📚 PERSONALIZED CURRICULUM (SINGLE PARTICIPANT)")
        print("=" * 60)

        # Check API key
        if not self.configuration.get_api_key("openrouter"):
            print("❌ OpenRouter API key required for curriculum generation")
            print("   Set OPENROUTER_API_KEY in .env file")
            return

        # Check participant data
        participants_csv = self.edition.participants_csv
        if not participants_csv.exists():
            print(f"❌ {self.edition.year} Participant data not found: {participants_csv}")
            return

        try:
            from symposium.analysis.participants import ParticipantAnalyzer
            from symposium.core.data_loader import DataLoader

            # Load participant data
            participants = DataLoader.load_participant_data(participants_csv)

            # Show available participants
            print(f"\n📊 Available participants ({len(participants)} total):")
            for i, name in enumerate(sorted(participants.keys())[:10], 1):
                print(f"   {i}. {name}")
            if len(participants) > 10:
                print(f"   ... and {len(participants) - 10} more")

            # Get participant name
            participant_name = input("\nEnter participant name (or partial match): ").strip()

            # Find matching participants
            matches = [
                name for name in participants.keys() if participant_name.lower() in name.lower()
            ]

            if not matches:
                print(f"❌ No participant found matching: {participant_name}")
                return
            elif len(matches) > 1:
                print("\n📋 Multiple matches found:")
                for i, name in enumerate(matches, 1):
                    print(f"   {i}. {name}")
                try:
                    choice = int(input("Choose participant (number): ").strip()) - 1
                except ValueError:
                    print("❌ Invalid number entered.")
                    return
                if not 0 <= choice < len(matches):
                    print("❌ Selection out of range.")
                    return
                participant_name = matches[choice]
            else:
                participant_name = matches[0]

            print(f"\n📚 Generating curriculum for {participant_name}...")

            # Create OpenRouter API client (Claude for curriculum)
            logger.info(f"Creating OpenRouter API client (Claude) for {participant_name}")
            client = self.create_api_client("openrouter")
            analyzer = ParticipantAnalyzer(client, self.config.get("data", {}))
            print("   🤖 Using OpenRouter Claude for curriculum")

            # Generate curriculum
            participant_data = participants[participant_name]
            curriculum = analyzer.generate_personalized_curriculum(participant_data)

            # Save result
            output_base = self.edition.output_dir / "single_curriculum"
            output_base.mkdir(parents=True, exist_ok=True)

            from symposium.io.writers import ReportWriter

            ReportWriter.save_participant_report(
                participant_name, curriculum, output_base, "curriculum"
            )

            print("✅ Curriculum generation completed!")
            print(f"📁 Results saved to: {output_base}/{participant_name}/")
            print("\n📄 Preview (first 300 chars):")
            print(f"   {(curriculum or '')[:300]}...")

        except Exception as e:
            logger.error(f"Curriculum generation failed: {e}")
            print(f"❌ Curriculum generation failed: {e}")

        print()

    def create_visualizations(self):
        """Create data visualizations."""
        print("🌐 CREATE VISUALIZATIONS")
        print("=" * 50)

        # Check for data to visualize
        data_dir = self.edition.output_dir / "people"

        if not data_dir.exists() or not any(data_dir.rglob("*.md")):
            print("❌ No analysis data found for visualization.")
            print(f"   Expected location: {data_dir}")
            print(f"   Run Option 2 (Analyze {self.edition.year} Participants) first.")
            return

        print(f"✅ Found data in: {data_dir}")
        print("\nAvailable visualization types:")
        print("1. 📊 Embeddings (PCA/LSA/t-SNE)")
        print("2. 🌐 Networks (Similarity networks)")
        print("3. 📈 Distributions (Statistical plots)")
        print("4. 🎯 All Visualizations")

        viz_types = ["embeddings", "networks", "distributions", "all"]
        while True:
            choice = input("Choose visualization type (1-4): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(viz_types):
                    viz_type = viz_types[idx]
                    break
                else:
                    print("❌ Please choose between 1 and 4")
            except ValueError:
                print("❌ Please enter a number.")

        print("\n🔄 Creating visualizations...")
        logger.info(f"Creating {viz_type} visualizations")

        # Call the visualization package functions in-process rather than shelling
        # out to the `symposium` console script (no dependency on it being on PATH,
        # and no subprocess overhead / capture issues).
        import argparse

        from symposium.cli.visualize import (
            visualize_all,
            visualize_distributions,
            visualize_embeddings,
            visualize_networks,
        )

        base = dict(
            input_dir=str(data_dir),
            output_dir=str(self.edition.output_dir / "visualizations"),
            method="pca",
            n_components=2,
            threshold=0.3,
            max_terms=50,
            max_features=5000,
            label=None,
            layout="spring",
            log_level="INFO",
        )

        try:
            if viz_type == "embeddings":
                method = input("Reduction method (pca/lsa/tsne, default: pca): ").strip() or "pca"
                visualize_embeddings(argparse.Namespace(**{**base, "method": method}))
            elif viz_type == "networks":
                layout = (
                    input(
                        "Network layout (spring/circular/kamada_kawai, default: spring): "
                    ).strip()
                    or "spring"
                )
                visualize_networks(argparse.Namespace(**{**base, "layout": layout}))
            elif viz_type == "distributions":
                visualize_distributions(argparse.Namespace(**base))
            else:  # all
                method = input("Embedding method (pca/lsa/tsne, default: pca): ").strip() or "pca"
                layout = (
                    input(
                        "Network layout (spring/circular/kamada_kawai, default: spring): "
                    ).strip()
                    or "spring"
                )
                visualize_all(argparse.Namespace(**{**base, "method": method, "layout": layout}))

            logger.info("Visualization completed successfully")
            print("✅ Visualization completed!")
            print(f"📁 Results saved to: {self.edition.output_dir}/visualizations/")
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            print(f"❌ Visualization failed: {e}")

        print()

    def manage_configuration(self):
        """Manage system configuration."""
        print("🔧 CONFIGURATION MANAGEMENT")
        print("=" * 50)

        print("Current configuration:")
        print(
            f"   Default API Provider: {self.config.get('api', {}).get('provider', 'perplexity')}"
        )
        print(
            f"   Perplexity Model: {self.config.get('api', {}).get('perplexity', {}).get('model', 'sonar')}"
        )
        print(
            f"   OpenRouter Model: {self.config.get('api', {}).get('openrouter', {}).get('model', 'anthropic/claude-3.5-sonnet')}"
        )

        # Check API keys
        from dotenv import load_dotenv

        load_dotenv(current_dir / ".env")

        perplexity_key = self.configuration.get_api_key("perplexity")
        openrouter_key = self.configuration.get_api_key("openrouter")

        print(f"   Perplexity API Key: {'✅ Set' if perplexity_key else '❌ Missing'}")
        print(f"   OpenRouter API Key: {'✅ Set' if openrouter_key else '❌ Missing'}")

        print("\nOptions:")
        print("1. Test API connectivity")
        print("2. View configuration details")
        print("3. Back to main menu")

        choice = input("Choose option (1-3): ").strip()

        if choice == "1":
            self.test_api_connectivity()
        elif choice == "2":
            self.show_config_details()

        print()

    def test_api_connectivity(self):
        """Test API connectivity."""
        print("\n🧪 Testing API connectivity...")

        try:
            providers = []
            if self.configuration.get_api_key("perplexity"):
                providers.append("perplexity")
            if self.configuration.get_api_key("openrouter"):
                providers.append("openrouter")

            if not providers:
                print("❌ No API keys configured")
                return

            for provider in providers:
                try:
                    client = self.create_api_client(provider)
                    response = client.get_response(
                        "Respond with 'test successful' if you receive this.",
                        "You are a helpful assistant.",
                    )
                    if "test successful" in response.lower():
                        print(f"✅ {provider} API: Connected successfully")
                    else:
                        print(f"❌ {provider} API: Unexpected response")
                except Exception as e:
                    print(f"❌ {provider} API: {e}")
        except ImportError as e:
            print(f"❌ Module import failed: {e}")

    def show_config_details(self):
        """Show detailed configuration."""
        print("\n📋 DETAILED CONFIGURATION")
        print("=" * 50)
        print(json.dumps(self.configuration.redacted_dict(), indent=2, default=str))

    def test_system_components(self):
        """Test all system components."""
        print("🧪 TEST SYSTEM COMPONENTS")
        print("=" * 50)

        # Test imports
        print("Testing imports...")
        try:
            import importlib

            from symposium.core.data_loader import DataLoader

            for module in (
                "symposium.analysis.participants",
                "symposium.core.api",
                "symposium.io.writers",
            ):
                importlib.import_module(module)

            print("✅ All imports successful")
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            print("   Run the setup script: ./symposium.sh")
            print("   Or manually: uv pip install -e .")
            return

        # Test configuration
        print("Testing configuration...")
        config = self.config
        api_ok = bool(config.get("api", {}).get("provider"))
        print(f"✅ Configuration loaded: {api_ok}")

        # Verify I/O in a unique owned directory, preserving existing organizer files.
        import tempfile

        self.edition.output_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="symposium-check-", dir=self.edition.output_dir
        ) as temporary:
            test_path = Path(temporary) / "test_io.txt"
            test_content = "Symposium I/O test"
            test_path.write_text(test_content, encoding="utf-8")
            io_ok = test_path.read_text(encoding="utf-8") == test_content
        print(f"✅ File I/O working: {io_ok}")

        # Test data loading
        print("Testing data loading...")
        participants_csv = self.edition.participants_csv
        if participants_csv.exists():
            try:
                from symposium.core.data_loader import DataLoader

                participants = DataLoader.load_participant_data(participants_csv)
                print(f"✅ Data loading successful: {len(participants)} participants")
            except Exception as e:
                print(f"❌ Data loading failed: {e}")
        else:
            print(f"⚠️  Participant data not found: {participants_csv}")

        print("\n🎯 COMPONENT TEST RESULTS:")
        print("   Imports: ✅")
        print(f"   Configuration: {'✅' if api_ok else '❌'}")
        print(f"   File I/O: {'✅' if io_ok else '❌'}")

        print()

    def run(self):
        """Run the selected edition's interactive interface."""
        logger.info("Starting Symposium interactive interface")
        self.display_header()

        while True:
            try:
                self.display_menu()
                choice = self.get_choice()
                logger.info(f"User selected option: {choice}")

                if choice == "1":
                    logger.info("Executing: list_available_data")
                    self.list_available_data()
                elif choice == "2":
                    logger.info("Executing: analyze_participants")
                    self.analyze_participants()
                elif choice == "3":
                    logger.info("Executing: generate_column_summaries")
                    self.generate_column_summaries()
                elif choice == "4":
                    logger.info("Executing: research_single_participant")
                    self.research_single_participant()
                elif choice == "5":
                    logger.info("Executing: generate_single_curriculum")
                    self.generate_single_curriculum()
                elif choice == "6":
                    logger.info("Executing: create_visualizations")
                    self.create_visualizations()
                elif choice == "7":
                    logger.info("Executing: manage_configuration")
                    self.manage_configuration()
                elif choice == "8":
                    logger.info("Executing: test_system_components")
                    self.test_system_components()
                elif choice == "9":
                    logger.info("User selected exit")
                    print("👋 Thank you for using Symposium!")
                    print(f"   Selected edition: {self.edition.year} Active Inference Symposium")
                    break

                # Pause before showing menu again
                input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                logger.info("User interrupted with Ctrl+C")
                print("\n\n👋 Thank you for using Symposium!")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                print(f"\n❌ Unexpected error: {e}")
                print("   Please report this issue if it persists.")
                input("\nPress Enter to continue...")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Interactive Symposium edition workflows")
    parser.add_argument("--year", type=int, help="Symposium edition (default: config or 2026)")
    parser.add_argument(
        "--config", type=Path, help="JSON config file (default: optional project config.json)"
    )
    args = parser.parse_args()
    if args.year is not None:
        try:
            Edition(year=args.year)
        except ValueError as exc:
            parser.error(str(exc))
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if args.config is not None:
        args.config = args.config.resolve()
    os.chdir(current_dir)
    logger.info("Starting Symposium interactive interface")

    try:
        logger.info("Initializing SymposiumRunner")
        runner = SymposiumRunner(year=args.year, config_file=args.config)
        logger.info("SymposiumRunner initialized successfully")
        runner.run()
    except KeyboardInterrupt:
        logger.info("User interrupted with Ctrl+C")
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you're in the symposium project directory")
        print("2. Run the setup script: ./symposium.sh")
        print("3. Or manually: uv pip install -e .")
        print("4. Set API keys in .env file")
        sys.exit(1)


if __name__ == "__main__":
    main()
