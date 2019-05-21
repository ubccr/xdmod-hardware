<?php

namespace ETL\Ingestor;

use ETL\aOptions;
use ETL\iAction;
use ETL\aAction;
use ETL\Configuration\EtlConfiguration;
use ETL\EtlOverseerOptions;

use Log;

class HostTableTransformIngestor extends pdoIngestor implements iAction
{

    private $_instance_state;
    private $_end_time;

    /**
     * @see ETL\Ingestor\pdoIngestor::__construct()
     */
    public function __construct(aOptions $options, EtlConfiguration $etlConfig, Log $logger = null)
    {
        parent::__construct($options, $etlConfig, $logger);

        $this->_end_time = $etlConfig->getVariableStore()->endDate ? date('Y-m-d H:i:s', strtotime($etlConfig->getVariableStore()->endDate)) : null;

        $this->resetInstance();
    }

    private function initInstance($srcRecord)
    {
        $default_end_time = isset($this->_end_time) ? $this->_end_time : $srcRecord['record_time'];

        $this->_instance_state = array(
            'host_id' => $srcRecord['host_id'],
            'node_id' => $srcRecord['node_id'],
            'start_time' => $srcRecord['record_time'],
            'start_day_id' => $srcRecord['record_day_id'],
            'end_time' => $srcRecord['record_time'],
            'end_day_id' => $srcRecord['record_day_id'],
        );
    }

    private function resetInstance()
    {
        $this->_instance_state = null;
    }

    private function updateInstance($srcRecord)
    {
        $this->_instance_state['end_time'] = $srcRecord['record_time'];
        $this->_instance_state['end_day_id'] = $srcRecord['record_day_id'];
    }

    /**
     * @see ETL\Ingestor\pdoIngestor::transform()
     */
    protected function transform(array $srcRecord, &$orderId)
    {

        // We want to just flush when we hit the dummy row
        if ($srcRecord['record_day_id'] === 0) {
            if (isset($this->_instance_state)) {
                return array($this->_instance_state);
            } else {
                return array();
            }
        }

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

    public function transformHelper(array $srcRecord)
    {
        return $this->transform($srcRecord, $orderId);
    }
}
