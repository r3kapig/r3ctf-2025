#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tiffio.h>

int main(int argc, char *argv[]) {
  if (argc != 3) {
    fprintf(stderr, "Usage: %s <output.tiff> <icc_profile.icc>\n", argv[0]);
    return 1;
  }

  const char *output_filename = argv[1];
  const char *icc_profile_filename = argv[2];

  // Create output TIFF file
  TIFF *output_tiff = TIFFOpen(output_filename, "w");
  if (!output_tiff) {
    fprintf(stderr, "Error: Cannot create output file %s\n", output_filename);
    return 1;
  }

  // Set output image properties: 1x1 image with 784 samples per pixel
  uint32_t width = 1;
  uint32_t height = 1;
  uint16_t samples_per_pixel = 784;
  uint16_t bits_per_sample = 8;

  TIFFSetField(output_tiff, TIFFTAG_IMAGEWIDTH, width);
  TIFFSetField(output_tiff, TIFFTAG_IMAGELENGTH, height);
  TIFFSetField(output_tiff, TIFFTAG_SAMPLESPERPIXEL, samples_per_pixel);
  TIFFSetField(output_tiff, TIFFTAG_BITSPERSAMPLE, bits_per_sample);
  TIFFSetField(output_tiff, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK);
  TIFFSetField(output_tiff, TIFFTAG_PLANARCONFIG, PLANARCONFIG_CONTIG);
  TIFFSetField(output_tiff, TIFFTAG_COMPRESSION, COMPRESSION_NONE);

  // Read and embed ICC profile
  FILE *icc_file = fopen(icc_profile_filename, "rb");
  if (!icc_file) {
    fprintf(stderr, "Error: Cannot open ICC profile file %s\n", icc_profile_filename);
    TIFFClose(output_tiff);
    return 1;
  }

  // Get ICC profile size
  fseek(icc_file, 0, SEEK_END);
  long icc_size = ftell(icc_file);
  fseek(icc_file, 0, SEEK_SET);

  if (icc_size <= 0) {
    fprintf(stderr, "Error: Invalid ICC profile file size\n");
    fclose(icc_file);
    TIFFClose(output_tiff);
    return 1;
  }

  // Allocate memory for ICC profile data
  unsigned char *icc_data = (unsigned char *)malloc(icc_size);
  if (!icc_data) {
    fprintf(stderr, "Error: Memory allocation failed for ICC profile\n");
    fclose(icc_file);
    TIFFClose(output_tiff);
    return 1;
  }

  // Read ICC profile data
  size_t bytes_read = fread(icc_data, 1, icc_size, icc_file);
  fclose(icc_file);

  if (bytes_read != (size_t)icc_size) {
    fprintf(stderr, "Error: Failed to read ICC profile data\n");
    free(icc_data);
    TIFFClose(output_tiff);
    return 1;
  }

  // Embed ICC profile in TIFF
  TIFFSetField(output_tiff, TIFFTAG_ICCPROFILE, (uint32_t)icc_size, icc_data);
  printf("ICC profile embedded: %s (%ld bytes)\n", icc_profile_filename, icc_size);

  // Handle extra samples to avoid warnings
  // For PHOTOMETRIC_MINISBLACK, we expect 1 color channel, so the rest are extra samples
  /*
  if (samples_per_pixel > 1) {
    uint16_t *extra_samples = (uint16_t *)malloc((samples_per_pixel - 1) * sizeof(uint16_t));
    if (extra_samples) {
      // Mark all extra samples as unspecified data
      for (uint16_t i = 0; i < samples_per_pixel - 1; i++) {
        extra_samples[i] = EXTRASAMPLE_UNSPECIFIED;
      }
      TIFFSetField(output_tiff, TIFFTAG_EXTRASAMPLES, samples_per_pixel - 1, extra_samples);
      free(extra_samples);
    }
  }

  printf("Creating empty TIFF image: %dx%d with %d samples per pixel\n", 
         width, height, samples_per_pixel);
  */

  // Allocate memory for empty pixel data (all zeros)
  size_t pixel_data_size = samples_per_pixel * (bits_per_sample / 8);
  unsigned char *pixel_data = (unsigned char *)calloc(pixel_data_size, 1);
  
  if (!pixel_data) {
    fprintf(stderr, "Error: Memory allocation failed\n");
    TIFFClose(output_tiff);
    return 1;
  }

  // Write the single scanline containing all 784 samples (all zeros)
  if (TIFFWriteScanline(output_tiff, pixel_data, 0, 0) < 0) {
    fprintf(stderr, "Error: Failed to write output scanline\n");
    free(pixel_data);
    TIFFClose(output_tiff);
    return 1;
  }

  // Clean up
  TIFFClose(output_tiff);
  free(pixel_data);
  free(icc_data);

  printf("Empty TIFF file created successfully!\n");
  printf("Output: %s (1x1 image with %d samples per pixel, all zeros)\n", 
         output_filename, samples_per_pixel);

  return 0;
}
