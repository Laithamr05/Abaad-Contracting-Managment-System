import { useState } from 'react'

/**
 * SafeImage - A robust image component with fallback, aspect-ratio, and error handling
 * 
 * @param {string} src - Image source (local or remote)
 * @param {string} alt - Alt text for accessibility
 * @param {string} className - Additional CSS classes
 * @param {string} objectFit - CSS object-fit value (cover, contain, fill, etc.)
 * @param {string|number} width - Image width
 * @param {string|number} height - Image height
 * @param {string|number} maxWidth - Maximum image width
 * @param {string} aspectRatio - CSS aspect-ratio value (e.g., "16/9", "1/1")
 * @param {string} fallbackSrc - Fallback image source if main image fails
 * @param {boolean} lazy - Enable lazy loading
 * @param {object} style - Additional inline styles
 */
const SafeImage = ({
  src,
  alt = '',
  className = '',
  objectFit = 'contain',
  width,
  height,
  maxWidth,
  aspectRatio,
  fallbackSrc = '/static/images/logo.png',
  lazy = true,
  style = {},
  ...props
}) => {
  const [imgSrc, setImgSrc] = useState(src || fallbackSrc)
  const [hasError, setHasError] = useState(false)

  const handleError = () => {
    if (!hasError && imgSrc !== fallbackSrc) {
      setHasError(true)
      setImgSrc(fallbackSrc)
    }
  }

  // Build style object
  const imageStyle = {
    objectFit,
    display: 'block',
    ...(width && { width: typeof width === 'number' ? `${width}px` : width }),
    ...(height && { height: typeof height === 'number' ? `${height}px` : height }),
    ...(maxWidth && { maxWidth: typeof maxWidth === 'number' ? `${maxWidth}px` : maxWidth }),
    ...(aspectRatio && !width && !height && { aspectRatio }),
    ...style
  }

  // If aspect-ratio is provided without width/height, use a wrapper
  if (aspectRatio && !width && !height) {
    return (
      <div
        className={`safe-image-wrapper ${className}`}
        style={{ aspectRatio, width: '100%', position: 'relative', overflow: 'hidden' }}
      >
        <img
          src={imgSrc}
          alt={alt}
          onError={handleError}
          loading={lazy ? 'lazy' : 'eager'}
          decoding="async"
          style={{
            ...imageStyle,
            width: '100%',
            height: '100%',
            position: 'absolute',
            top: 0,
            left: 0
          }}
          {...props}
        />
      </div>
    )
  }

  return (
    <img
      src={imgSrc}
      alt={alt}
      className={className}
      onError={handleError}
      loading={lazy ? 'lazy' : 'eager'}
      decoding="async"
      style={imageStyle}
      {...props}
    />
  )
}

export default SafeImage
