# Example JSON Files for Testing

This directory contains example JSON files for testing the batch upload functionality.

## Campaign Examples

### `campaign-complete.json`
Complete campaign with all required fields. Can be imported directly.

### `campaign-incomplete.json`
Incomplete campaign missing `target_region` and `target_audience`. Will trigger the form to complete missing fields.

## Product Examples

### `products-batch.json`
Array of 3 products for batch import. Note: `campaign_id` will be added automatically based on the selected campaign.

### `product-single.json`
Single product for import. Missing `campaign_id` will be added based on context.

## Notes

- Image URLs in these examples use `picsum.photos` for demo purposes
- The backend will automatically download these images and store them locally
- Database entries will be updated with local paths (e.g., `/static/media/image_uuid.jpg`)
- If JSON is incomplete, the UI will switch to manual form with pre-filled data

## Testing Flow

1. **Complete Campaign**: Upload `campaign-complete.json` → Should create immediately
2. **Incomplete Campaign**: Upload `campaign-incomplete.json` → Form appears with pre-filled message and brand images
3. **Batch Products**: Select a campaign, upload `products-batch.json` → Creates 3 products with downloaded images
4. **Single Product**: Upload `product-single.json` → Creates 1 product
