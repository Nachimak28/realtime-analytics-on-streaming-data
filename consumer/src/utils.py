from datetime import datetime
from pytz import timezone
from config import _logger, redis_conn

def get_current_time():
    # Getting current time with indian timezone
    india_tz = timezone('Asia/Kolkata')
    time = datetime.now(india_tz)
    ist_time = time.strftime('%Y-%m-%d_%H-%M-%S')
    return ist_time

# incremental mean and std class
class IncrementalAnalytics:
    def __init__(self, redis_conn, log=False):
        # check if key exists
        self.redis_conn = redis_conn
        self.log = log
        self.data = {}
    
    def _process_data(self):
        if isinstance(self.data, dict) and self.data != {}:
            print('here')
            processed_dict = {}
            for k, v in self.data.items():
                print(k, v)
                processed_dict[k.decode("utf-8")] = float(v)
            self.data = processed_dict


    def _get_sensor_data(self, sensor_key):
        self.data = self.redis_conn.hgetall(sensor_key)
        if self.data == {}:
            # set default values and initialize the object
            self.data = {"mean": 0, "std_dev": 0, "pre_division_variance": 0, "variance": 0, "stream_length": 1}
            self.redis_conn.hmset(sensor_key, self.data)
        else:
            self._process_data()
            if self.log:
                _logger.info(self.data)
    
    def update(self, sensor_key, new_value):
        # check if sensor key exists, if not then initiaize with default values 
        # else retrieve values for given sensor
        self._get_sensor_data(sensor_key=sensor_key)

        try:
            previous_mean = self.data.get('mean', 0)
            previous_pre_division_variance = self.data.get('pre_division_variance', 0)
            stream_length = self.data.get('stream_length', 1)
            
            self.data['mean'] = previous_mean + (new_value - previous_mean)/stream_length
            self.data['pre_division_variance'] = previous_pre_division_variance + ((new_value - self.data['mean']) *(new_value - previous_mean))
            self.data['stream_length'] += 1
            self.data['variance'] = self.data['pre_division_variance']/(self.data['stream_length'] - 1)
            self.data['std_dev'] = (self.data['variance'])**0.5
            
            
            self.redis_conn.hset(sensor_key, 'mean', self.data['mean'])
            self.redis_conn.hset(sensor_key, 'pre_division_variance', self.data['pre_division_variance'])
            self.redis_conn.hset(sensor_key, 'variance', self.data['variance'])
            self.redis_conn.hset(sensor_key, 'std_dev', self.data['std_dev'])
            self.redis_conn.hincrby(sensor_key, 'stream_length', amount=1)

            _logger.info('Data updated successfully')

            return self.data
        except Exception as e:
            _logger.exception(str(e))
            return {}

# initialize the object
inc_analytics = IncrementalAnalytics(redis_conn=redis_conn, log=False)


