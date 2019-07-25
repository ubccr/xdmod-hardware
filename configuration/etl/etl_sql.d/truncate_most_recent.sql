SET @minTime = (SELECT min(record_time_ts) FROM mod_hardware.staging);

-- TODO: Check if these tables exist

DELETE FROM mod_hardware.record_time_staging WHERE (record_time_ts >= @minTime);

DELETE FROM mod_hardware.host WHERE (unix_timestamp(start_time) >= @minTime);