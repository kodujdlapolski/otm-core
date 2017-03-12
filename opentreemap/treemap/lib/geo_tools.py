import pyproj


class ProjectionConverter(object):

    wgs84 = pyproj.Proj(init='EPSG:4326')
    webmercator = pyproj.Proj(init='EPSG:3857')

    def to_wgs84(self, lon, lat):
        return pyproj.transform(self.webmercator, self.wgs84, lon, lat)

    def to_webmercator(self, lon, lat):
        return pyproj.transform(self.wgs84, self.webmercator, lon, lat)
