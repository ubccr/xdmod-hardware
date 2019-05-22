<?php
/**
* This class iterates over a staging table (record_time_staging) in which each row pairs a 
* host with a hardware configuration at a specific time (record_time). 
* The transformation will associate each host with a specific hardware configuration
* over a *range* of times (start_time and end_time)
* 
* @author Max Dudek <maxdudek@gmail.com>
* @date 2019-05-20
*/


namespace ETL\Ingestor;

use ETL\aOptions;
use ETL\iAction;
use ETL\aAction;
use ETL\Configuration\EtlConfiguration;
use ETL\EtlOverseerOptions;

use Log;

class HostTableTransformIngestor extends pdoIngestor implements iAction
{

    /**
     * @var $_instance_state an array representing a row to be added to the host table - 
     * it associates a host with a hardware configuration during a period of time
     */
    private $_instance_state;

    /**
     * @see ETL\Ingestor\pdoIngestor::__construct()
     */
    public function __construct(aOptions $options, EtlConfiguration $etlConfig, Log $logger = null)
    {
        parent::__construct($options, $etlConfig, $logger);

        $this->_instance_state = null;
    }

    /**
     * Create a new row and associate it with the current record on the staging table
     * 
     * @param $srcRecord the current row from the staging table being read
     */
    private function initInstance(array $srcRecord)
    {
        $this->_instance_state = array(
            'host_id' => $srcRecord['host_id'],
            'node_id' => $srcRecord['node_id'],
            'start_time' => $srcRecord['record_time'],
            'start_day_id' => $srcRecord['record_day_id'],
            'end_time' => $srcRecord['record_time'],
            'end_day_id' => $srcRecord['record_day_id'],
        );
    }

    /**
     * Update the end_time of the current instance_state to match with the current record
     * 
     * @param $srcRecord the current row from the staging table being read
     */
    private function updateInstance(array $srcRecord)
    {
        $this->_instance_state['end_time'] = $srcRecord['record_time'];
        $this->_instance_state['end_day_id'] = $srcRecord['record_day_id'];
    }

    /**
     * @see ETL\Ingestor\pdoIngestor::transform()
     * 
     * This function gets called on every row in the record_time_staging table.
     * If the row represents a new hardware/host pairing, then a new instance will be created.
     * Otherwise, the current instance will be updated.
     * 
     * @param $srcRecord The current row from the staging table
     * 
     * @return array The final instance_state if the hardware changes, 
     * or an empty array otherwise
     */
    protected function transform(array $srcRecord, &$orderId)
    {

        // We want to just flush when we hit the dummy row
        if ($srcRecord['host_id'] === 0) {
            if (isset($this->_instance_state)) {
                return array($this->_instance_state);
            } else {
                return array();
            }
        }

        // Initially, the instance_state is null
        if ($this->_instance_state === null) {
            $this->initInstance($srcRecord);
        }

        $transformedRecord = array();

        // If the host or the node changes, create a new instance
        if (($this->_instance_state['node_id'] !== $srcRecord['node_id']) || ($this->_instance_state['host_id'] !== $srcRecord['host_id'])) {
            $transformedRecord[] = $this->_instance_state;
            $this->initInstance($srcRecord);
        } else {
            $this->updateInstance($srcRecord);
        }
        return $transformedRecord;
    }

    /**
     * Generates an SQL query which is used on the staging table (record_time_staging)
     * to generate the source table which is iterated through. A dummy row of zeros is added
     * at the end, and the table is sorted by host and time.
     * 
     * @return string the SQL query
     */
    protected function getSourceQueryString()
    {
        $sql = parent::getSourceQueryString();

        // Due to the way the Finite State Machine handles the rows in event reconstruction, the last row
        // is lost. To work around this we add a dummy row filled with zeroes.
        $colCount = count($this->etlSourceQuery->records);
        $unionValues = array_fill(0, $colCount, 0);

        $sql = $sql . "\nUNION ALL\nSELECT " . implode(',', $unionValues) . "\nORDER BY host_id DESC, record_time";

        return $sql;
    }
}
