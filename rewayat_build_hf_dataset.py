import os
import pandas as pd
from datasets import Dataset, DatasetDict
from huggingface_hub import login, HfApi
from dotenv import load_dotenv
import glob

load_dotenv()

def load_and_combine_tsvs(tsv_folder_path, pattern="*.tsv"):
    """
    Load multiple TSV files and combine them into a single dataset
    
    Args:
        tsv_folder_path (str): Path to folder containing TSV files
        pattern (str): File pattern to match (default: "*.tsv")
    
    Returns:
        pd.DataFrame: Combined dataframe
    """
    tsv_files = glob.glob(os.path.join(tsv_folder_path, pattern))
    
    if not tsv_files:
        raise ValueError(f"No TSV files found in {tsv_folder_path}")
    
    dataframes = []
    for file in tsv_files:
        print(f"Loading {file}...")
        df = pd.read_csv(file, sep="\t")
        # Add source file column (optional)
        df['source_file'] = os.path.basename(file)
        dataframes.append(df)
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    print(f"Combined {len(tsv_files)} TSV files into dataset with {len(combined_df)} rows")
    
    return combined_df

def create_train_valid_split(df, valid_ratio=1/1000, random_state=42):
    """
    Create train/validation split for the dataset with 1000:1 ratio
    
    Args:
        df (pd.DataFrame): Input dataframe
        valid_ratio (float): Proportion for validation set (1/1000 = 0.001)
        random_state (int): Random seed
    
    Returns:
        DatasetDict: Dictionary with train/valid splits
    """
    from sklearn.model_selection import train_test_split
    
    train_df, valid_df = train_test_split(df, test_size=valid_ratio, random_state=random_state)
    
    # Convert to Hugging Face datasets
    train_dataset = Dataset.from_pandas(train_df)
    valid_dataset = Dataset.from_pandas(valid_df)
    
    dataset_dict = DatasetDict({
        'train': train_dataset,
        'validation': valid_dataset
    })
    
    return dataset_dict

def create_dataset_from_tsvs(tsv_folder_path, split_data=True):
    """
    Create Hugging Face dataset from TSV files
    
    Args:
        tsv_folder_path (str): Path to TSV files
        split_data (bool): Whether to create train/validation split
    
    Returns:
        Dataset or DatasetDict: Processed dataset
    """
    # Load and combine TSVs
    combined_df = load_and_combine_tsvs(tsv_folder_path)
    
    # Clean data (customize as needed)
    print("Cleaning data...")
    combined_df = combined_df.dropna()  # Remove null values
    combined_df = combined_df.drop_duplicates()  # Remove duplicates
    
    if split_data:
        return create_train_valid_split(combined_df)
    else:
        return Dataset.from_pandas(combined_df)

def publish_to_huggingface(dataset, repo_name, description="", private=False, token=None):
    """
    Publish dataset to Hugging Face Hub
    
    Args:
        dataset: Dataset or DatasetDict to publish
        repo_name (str): Repository name (username/dataset-name)
        description (str): Dataset description
        private (bool): Whether repository should be private
        token (str): Hugging Face token (optional if logged in)
    
    Returns:
        str: Repository URL
    """
    # Login if token provided
    if token:
        login(token=token)
    
    # Create repository and upload dataset
    print(f"Publishing dataset to {repo_name}...")
    
    try:
        dataset.push_to_hub(
            repo_id=repo_name,
            private=private
        )
        
        # Add dataset card (README.md) with metadata
        api = HfApi()
        # Calculate dataset statistics
        if isinstance(dataset, Dataset):
            total_samples = len(dataset)
            features = list(dataset.features.keys())
        else:
            total_samples = sum(len(split) for split in dataset.values())
            features = list(next(iter(dataset.values())).features.keys())
            
        dataset_card = f"""---
license: mit
task_categories:
- other
language:
- ar
size_categories:
- 1K<n<10K
---

# {repo_name.split('/')[-1]}

{description}

## Dataset Description

This dataset was created from multiple TSV files and contains Arabic text fragments with the following information:

- **Total samples**: {total_samples}
- **Features**: {list(features)}
- **Splits**: train, validation (1000:1 ratio)

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{repo_name}")

# Access train split
train_data = dataset['train']

# Access validation split  
validation_data = dataset['validation']
```

## Data Fields

- **text**: Arabic text fragments with multiple punctuation marks
- **source_file**: Original source file name

## Citation

If you use this dataset, please cite it appropriately.
"""
        
        api.upload_file(
            path_or_fileobj=dataset_card.encode(),
            path_in_repo="README.md",
            repo_id=repo_name,
            repo_type="dataset"
        )
        
        repo_url = f"https://huggingface.co/datasets/{repo_name}"
        print(f"Dataset published successfully: {repo_url}")
        return repo_url
        
    except Exception as e:
        print(f"Error publishing dataset: {e}")
        raise

# Main execution function
def main():
    """
    Main function to create and publish dataset with train/validation splits
    """
    # Configuration
    TSV_FOLDER = "rewayat_tsv"  # Update this path
    REPO_NAME = "lliryc/rewayat"  # Update this
    DESCRIPTION = "Rewayat text fragments with train/validation splits"
    HF_TOKEN = os.getenv("HF_TOKEN")  # Or set as environment variable
    
    # Step 1: Create dataset from TSVs with train/validation splits
    print("Creating dataset from TSV files with train/validation splits...")
    dataset = create_dataset_from_tsvs(TSV_FOLDER, split_data=True)
    
    # Step 2: Preview dataset
    print("\nDataset preview:")
    print(f"Train samples: {len(dataset['train'])}")
    print(f"Validation samples: {len(dataset['validation'])}")
    print(f"Total samples: {len(dataset['train']) + len(dataset['validation'])}")
    print(f"Features: {list(dataset['train'].features.keys())}")
    print("\nSample train data:")
    print(dataset['train'][0])
    print("\nSample validation data:")
    print(dataset['validation'][0])
    
    # Step 3: Publish to Hugging Face
    repo_url = publish_to_huggingface(
        dataset=dataset,
        repo_name=REPO_NAME,
        description=DESCRIPTION,
        private=True,  # Set to True for private dataset
        token=HF_TOKEN
    )
    
    print(f"\n✅ Dataset successfully published at: {repo_url}")

# Example usage for specific scenarios
def example_usage():
    """
    Example usage patterns
    """
    
    # Example 1: Simple dataset without train/test split
    df = load_and_combine_tsvs("rewayat_tsv", "*.tsv")
    simple_dataset = Dataset.from_pandas(df)
    
    # Example 2: Custom preprocessing
    def custom_preprocessing(df):
        # Add your custom preprocessing here
        df['text_length'] = df['text'].str.len()  # Example feature engineering
        return df
    
    # Example 3: Multiple CSV files with different structures
    # You might need to standardize columns before combining
    
    # Example 4: Large datasets - use streaming
    # For very large datasets, consider using streaming=True when loading

if __name__ == "__main__":
    # Before running, install required packages:
    # pip install datasets huggingface_hub pandas scikit-learn
    
    main()