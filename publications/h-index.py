def calculate_h_index(citations):
    # Sort the citations in descending order
    sorted_citations = sorted(citations, reverse=True)
    
    # Find the h-index by looking for the last position where
    # the citation count is greater than or equal to the position (index + 1)
    for h, citation in enumerate(sorted_citations):
        if citation < h + 1:
            return h
    return len(sorted_citations)  # All papers have enough citations

# Example usage
if __name__ == "__main__":
    # Replace this list with the citation counts of your papers
    citation_counts = [3,2,5,2,5,16,5,16,3,6,1, 67]

    # Calculate h-index
    h_index = calculate_h_index(citation_counts)

    # Print the h-index
    print(f"The h-index is: {h_index}")
