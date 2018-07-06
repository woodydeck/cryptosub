import 'react-dates/initialize';
import 'react-dates/lib/css/_datepicker.css';
import React from 'react'
import { Segment, Grid, Header } from 'semantic-ui-react'
import { DateRangePicker } from 'react-dates';

const ChartHeader = ({startDate, endDate, handleDateChange, focusedInput, handleFocusChange}) => (
    <Grid verticalAlign='middle' columns='equal'>
        <Grid.Row>
            <Grid.Column>
            </Grid.Column>
            <Grid.Column textAlign='center'>
                <DateRangePicker
                    showClearDates={true}
                    small={true}
                    displayFormat="DD MMM  YY"
                    isOutsideRange={() => false}
                    startDate={startDate}
                    startDateId="startDate"
                    endDate={endDate}
                    endDateId="endDate"
                    onDatesChange={({ startDate, endDate }) => { handleDateChange(startDate, endDate) }}
                    focusedInput={focusedInput}
                    onFocusChange={focusedInput => { handleFocusChange(focusedInput) }}
                />
            </Grid.Column>
        </Grid.Row>
    </Grid>
)
export default ChartHeader
