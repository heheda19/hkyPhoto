import EXIF from 'exif-js'

export function readExif(file) {
  return new Promise((resolve) => {
    EXIF.getData(file, function () {
      const lat = EXIF.getTag(this, 'GPSLatitude')
      const latRef = EXIF.getTag(this, 'GPSLatitudeRef')
      const lon = EXIF.getTag(this, 'GPSLongitude')
      const lonRef = EXIF.getTag(this, 'GPSLongitudeRef')
      const takenAt = EXIF.getTag(this, 'DateTimeOriginal')

      let latitude = null, longitude = null
      if (lat && lon) {
        latitude = dmsToDecimal(lat) * (latRef === 'S' ? -1 : 1)
        longitude = dmsToDecimal(lon) * (lonRef === 'W' ? -1 : 1)
      }

      let takenAtISO = null
      if (takenAt) {
        takenAtISO = takenAt.replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3')
      }

      resolve({ latitude, longitude, takenAt: takenAtISO })
    })
  })
}

function dmsToDecimal(dms) {
  return dms[0] + dms[1] / 60 + dms[2] / 3600
}
