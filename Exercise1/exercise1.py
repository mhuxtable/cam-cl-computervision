# coding: utf-8

# Required imports.
import cv2, numpy as np, os

## ---------------------------------------------------------------------


## Exercise 1.1
def basic_convolution(image, kernel, verbose=False):
  'Computes the convolution of an image with a kernel.'
  # Allocate memory for result.
  result = np.zeros_like(image)
  
  # Image and kernel dimensions.
  (iend, jend) = image.shape
  (mend, nend) = kernel.shape
  
  # Iterate over all pixels in the image
  for i in range(mend - 1, iend):
    for j in range(nend - 1, jend):
      sum = float(0)
      for m in range(0, mend):
        for n in range(0, nend):
          sum += kernel[m][n] * image[i-m][j-n]

      # kernel already normalised, so / (mend * nend) factor omitted
      result[i][j] = sum
    if verbose: print "basic_convolution: Filtering row %3i of %i ..." % (i + 1, iend)
  
  return result


## Exercise 1.2
def padded_convolution(image, kernel, verbose=False):
  'Computes the convolution of an image with a kernel, with clamp-to-edge.'
  print "padded_convolution: Computing the padded convolution of the image."
  border=5
  ## TODO
  ## Enlarge the image so that there is information in the previously invalid areas
  # Expand by 5 pixels in every direction. Then take the convolution, which will produce
  # a 10 pixel wide border around the side which is removed later.
  expanded = cv2.copyMakeBorder(image, border,border,border,border, cv2.BORDER_WRAP);  
  
  ## Perform a convolution on this image
  convolved = basic_convolution(expanded, kernel, verbose)
  
  ## Return the centred result
  (x,y) = convolved.shape
  # Cut off the 10 pixel wide black edge from the return of the convolution
  # (10x10 as the kernel is 10x10, and we don't convolve at the edge as (0,0)
  # is not the centre of the kernel but the corner)
  return convolved[border*2:, border*2:]


## Exercise 1.3
def basic_convolution_dft(image, kernel, verbose=False):
  'Computes the convolution of an image with a kernel using a basic DFT-based approach.'
   
  print "basic_convolution_dft: Computing the DFT-based convolution of the image."

  output = np.zeros(image.shape, 'float')

  kernelpad = np.zeros_like(image)
  (x,y) = kernel.shape
  kernelpad[:x,:y] = kernel
  ## TODO
  ## Implementation of convolution theorem
  imagefft = np.fft.fft2(image)
  kernelfft = np.fft.fft2(kernelpad)

  resultfft = np.zeros_like(imagefft)
  (iend, jend) = imagefft.shape
  (mend, nend) = kernelfft.shape
  
  resultfft = np.multiply(imagefft, kernelfft)
  
  output = np.fft.ifft2(resultfft)
  output = np.absolute(output)
  
  ## Return the result.
  if output.dtype == np.complex128:
    raise Exception("Output image is complex valued.")
  return output
  

## Exercise 1.4
def padded_convolution_dft(image, kernel, verbose=False):
  'Computes the convolution of an image with a kernel using a DFT-based approach (clamp-to-edge).'
  
  print "padded_convolution_dft: Computing the padded DFT-based convolution of the image."

  ## TODO
  ## Implementation of convolution theorem with padding
  border=5
  ## TODO
  ## Enlarge the image so that there is information in the previously invalid areas
  # Expand by 5 pixels in every direction. Then take the convolution, which will produce
  # a 10 pixel wide border around the side which is removed later.
  expanded = cv2.copyMakeBorder(image, border,border,border,border, cv2.BORDER_WRAP);  
  
  ## Perform a convolution on this image
  convolved = basic_convolution_dft(expanded, kernel, False)
  
  ## Return the centred result
  (x,y) = convolved.shape
  # Cut off the 10 pixel wide black edge from the return of the convolution
  # (10x10 as the kernel is 10x10, and we don't convolve at the edge as (0,0)
  # is not the centre of the kernel but the corner)
  output = convolved[border*2:, border*2:]

  ## Return the result.
  if output.dtype == np.complex128:
    raise Exception("Output image is complex valued.")
  return output
  
  
  
## ---------------------------------------------------------------------

def show(name, im):
  if im.dtype == np.complex128:
    raise Exception("OpenCV can't operate on complex valued images")
  cv2.namedWindow(name)
  cv2.imshow(name, im)
  cv2.waitKey(1)
  
def are_similar(image, answer):
  if image.shape != answer.shape:
    return False
  diff = image - answer
  if np.max(np.abs(diff)) > 0.05:
    # Maximum 5% per-pixel difference
    return False
  if np.average(np.abs(diff)) > 0.01:
    # Maximum 1% average pixel difference
    return False
  return True

if __name__ == '__main__':

  verbose = True
  
  ## Start background thread for event handling of windows.
  if verbose:
    cv2.namedWindow("image")
    cv2.startWindowThread()
  
  ## Read in example image (greyscale, float, half-size).
  image = cv2.imread("input/mandrill.png", 0) / 255.0
  image = cv2.resize(image, (256, 256))
  if verbose: show("image", image)
  
  ## Prepare small convolution kernel (good for naive convolution).
  kernel = np.array([[0,0,0,0,5,5,5,5,5,5],
                     [0,0,0,5,1,1,1,1,1,5],
                     [0,0,5,1,1,1,1,1,1,5],
                     [0,5,1,1,1,1,1,1,1,5],
                     [5,1,1,1,1,1,1,1,1,5],
                     [5,1,1,1,1,1,1,1,1,5],
                     [0,5,1,1,1,1,1,1,1,5],
                     [0,0,5,1,1,1,1,1,1,5],
                     [0,0,0,5,1,1,1,1,1,5],
                     [0,0,0,0,5,5,5,5,5,5]], dtype=float)
  kernel = kernel / kernel.sum() # normalise kernel
  
  ## Prepare large convolution kernel (good for DFT-based convolution).
  #sigma = 10
  #gauss = cv2.getGaussianKernel(2 * 3 * sigma + 1, sigma)
  #kernel = np.outer(gauss, gauss)

  if verbose: print "kernel = %i x %i" % kernel.shape
  
  result1 = basic_convolution(image, kernel, verbose=verbose)
  #result1 = np.zeros_like(image)
  if verbose: show("Result 1 (basic)", result1)
  result2 = padded_convolution(image, kernel, verbose=verbose)
  #result2 = np.zeros_like(image)

  if verbose: show("Result 2 (padded)", result2)
  result3 = basic_convolution_dft(image, kernel, verbose=verbose)
  if verbose: show("Result 3 (basic DFT)", result3)
  result4 = padded_convolution_dft(image, kernel, verbose=verbose)
  if verbose: show("Result 4 (padded DFT)", result4)

  ## Save images to disk for comparison.
  cv2.imwrite(os.path.expanduser("image-input.png"), np.uint8(255 * image))
  cv2.imwrite(os.path.expanduser("image-basic_convolution.png"), np.uint8(255 * result1))
  cv2.imwrite(os.path.expanduser("image-padded_convolution.png"), np.uint8(255 * result2))
  cv2.imwrite(os.path.expanduser("image-basic_convolution-dft.png"), np.uint8(255 * result3))
  cv2.imwrite(os.path.expanduser("image-padded_convolution-dft.png"), np.uint8(255 * result4))
  
  ## Check the answers
  
  result1_correct = cv2.imread(os.path.expanduser("answer-images/image-basic_convolution.png"), 0) / 255.0
  if are_similar(result1, result1_correct):
    print "Exercise 1.1: CORRECT"
  else:
    print "Exercise 1.1: INCORRECT"
    if np.all(result1 == 0):
      print "    Result is all zeros."
    if result1.shape != result1_correct.shape:
      print "    The size is incorrect. The result should be the same size as the input"
      
  result2_correct = cv2.imread(os.path.expanduser("answer-images/image-padded_convolution.png"), 0) / 255.0
  if are_similar(result2, result2_correct):
    print "Exercise 1.2: CORRECT"
  else:
    print "Exercise 1.2: INCORRECT"
    if np.all(result2 == 0):
      print "    Result is all zeros."
    if result2.shape != result2_correct.shape:
      print "    The size is incorrect. The result should be the same size as the input"

  result3_correct = cv2.imread(os.path.expanduser("answer-images/image-basic_convolution-dft.png"), 0) / 255.0
  if are_similar(result3, result3_correct):
    print "Exercise 1.3: CORRECT"
  else:
    print "Exercise 1.3: INCORRECT"
    if result3.shape != result3_correct.shape:
      print "    The size is incorrect. The result should be the same size as the input"
      
  result4_correct = cv2.imread(os.path.expanduser("answer-images/image-padded_convolution-dft.png"), 0) / 255.0
  if are_similar(result4, result4_correct):
    print "Exercise 1.4: CORRECT"
  else:
    print "Exercise 1.4: INCORRECT"
    if result4.shape != result4_correct.shape:
      print "    The size is incorrect. The result should be the same size as the input"
      
  
  ## wait for keyboard input or windows to close
  if verbose:
    import sys, select 
    print "Press enter or any key on one of the images to exit"
    while True:
      if cv2.waitKey(100) != -1:
        break
      # http://stackoverflow.com/questions/1335507/keyboard-input-with-timeout-in-python
      i, o, e = select.select( [sys.stdin], [], [], 0.1 )
      if i:
        break
       
