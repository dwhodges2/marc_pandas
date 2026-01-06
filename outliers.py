import numpy as np
import pandas as pd


def main():
    # test code here
    s = pd.Series(
        [
            "short",
            "medium length",
            "another medium",
            "brief",
            "extremely long outlier string that skews the data significantly",
        ]
    )

    x = test(s)
    print(x)
    quit()


def test(series):
    # 2. Calculate the lengths
    lengths = series.str.len()
    print(f"String lengths: {lengths.tolist()}")

    # 3. Calculate IQR and thresholds
    Q1 = lengths.quantile(0.25)
    Q3 = lengths.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    print(f"Lower bound for outliers: {lower_bound}")
    print(f"Upper bound for outliers: {upper_bound}")

    # 4. Identify outliers using boolean masking
    is_outlier = (lengths < lower_bound) | (lengths > upper_bound)

    # 5. Get the outlier lengths
    outlier_lengths = lengths[is_outlier]
    print(f"\nOutlier lengths identified: {outlier_lengths.tolist()}")

    # 6. Get the original strings that are outliers
    outlier_strings = series[is_outlier]
    print("\nOutlier strings:")
    print(outlier_strings)


def find_outlier_strings(series, std_multiplier=2):
    if not series:
        return None

    # Calculate string lengths
    # lengths = [len(s) for s in string_list]
    lengths = series.str.len()

    # Calculate average length and standard deviation
    average_length = np.mean(lengths)
    std_dev = np.std(lengths)

    # Define thresholds for outlier detection
    upper_threshold = average_length + (std_multiplier * std_dev)
    lower_threshold = average_length - (std_multiplier * std_dev)

    # Identify outlier strings
    longer_strings = []
    shorter_strings = []

    for s in string_list:
        string_length = len(s)
        if string_length > upper_threshold:
            longer_strings.append(s)
        elif string_length < lower_threshold:
            shorter_strings.append(s)

    # return longer_strings, shorter_strings
    return {
        "long_outliers": longer_strings,
        "short_outliers": shorter_strings,
        "all_string_count": len(string_list),
        "long_count": len(longer_strings),
        "short_count": len(shorter_strings),
        "average_length": float(average_length),
        "std_dev": float(std_dev),
    }


def find_outlier_strings_bak(string_list, std_multiplier=2):
    if not string_list:
        return None

    # Calculate string lengths
    lengths = [len(s) for s in string_list]

    # Calculate average length and standard deviation
    average_length = np.mean(lengths)
    std_dev = np.std(lengths)

    # Define thresholds for outlier detection
    upper_threshold = average_length + (std_multiplier * std_dev)
    lower_threshold = average_length - (std_multiplier * std_dev)

    # Identify outlier strings
    longer_strings = []
    shorter_strings = []

    for s in string_list:
        string_length = len(s)
        if string_length > upper_threshold:
            longer_strings.append(s)
        elif string_length < lower_threshold:
            shorter_strings.append(s)

    # return longer_strings, shorter_strings
    return {
        "long_outliers": longer_strings,
        "short_outliers": shorter_strings,
        "all_string_count": len(string_list),
        "long_count": len(longer_strings),
        "short_count": len(shorter_strings),
        "average_length": float(average_length),
        "std_dev": float(std_dev),
    }


if __name__ == "__main__":
    main()
