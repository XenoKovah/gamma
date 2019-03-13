import React from 'react';

import PropTypes from 'prop-types';
import 'date-fns';

import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import TextField from '@material-ui/core/TextField';
import { Divider } from '@material-ui/core';
import Button from '@material-ui/core/Button';

import FormGroup from '@material-ui/core/FormGroup';
import InputBase from '@material-ui/core/InputBase';

import { MuiPickersUtilsProvider, TimePicker, DatePicker } from 'material-ui-pickers';
import Grid from '@material-ui/core/Grid';
import DateFnsUtils from '@date-io/date-fns';

import "react-datepicker/dist/react-datepicker.css";


export default class Filter extends React.Component {
    constructor(props) {
        super(props);

        this.handleChange = this.handleChange.bind(this);
        this.handleChangeDateStart = this.handleChangeDateStart.bind(this);
        this.handleChangeDateEnd = this.handleChangeDateEnd.bind(this);
        this.handleChangeInput = this.handleChangeInput.bind(this);
        this.clearStart = this.clearStart.bind(this);
        this.clearEnd = this.clearEnd.bind(this);
        this.removeFilter = this.removeFilter.bind(this);

        // let start = props.interval && props.interval.start ? props.interval.start.toISOString() : new Date().toISOString();
        // let end = props.interval && props.interval.end ? props.interval.end.toISOString() : new Date().toISOString();
        // this.state = {
        //     start: start,
        //     end: end,
        //     frequency: props.frequency,
        //     org: props.org
        // }
        console.log('Filter', props);
        
    }

    clearEnd(event) {
        this.setState({
            end: null
        }, () => {
            this.props.onChange(this.props.id, "end", null);
        })
    }

    removeFilter(event) {
        this.props.removeFilter(this.props.id);
    }

    clearStart(event) {
        this.setState({
            start: null
        }, () => {
            this.props.onChange(this.props.id, "start", null);
        })
    }

    handleChange(key, value) {
        this.props.onChange(this.props.id, key, value);
    }

    handleChangeDateStart(date) {
        let formattedDate = date.toISOString();
        this.setState({
            start: formattedDate
        }, () => {
            this.props.onChange(this.props.id, "start", formattedDate);
        })
    }

    handleChangeDateEnd(date) {
        let formattedDate = date.toISOString();
        this.setState({
            end: formattedDate
        }, () => {
            this.props.onChange(this.props.id, "end", formattedDate);
        })
    }

    handleChangeInput (event) {
        let state = {};
        let name = event.currentTarget.name;
        let value = event.currentTarget.value;
        state[name] = value;
        this.setState(state, () => {
            this.props.onChange(this.props.id, name, value);
        });
    }

    render() {
        let start = this.props && this.props.interval && this.props.interval.start ? this.props.interval.start : null;
        let end = this.props && this.props.interval && this.props.interval.end ? this.props.interval.end : null;
        return (
            <div>
                <h3>Filters</h3>
                <FormGroup>

                <InputLabel htmlFor="org">Org</InputLabel>
                    <Input name="org" id="org"
                        value={this.props.org}
                        onChange={this.handleChangeInput}
                        />
                <InputLabel htmlFor="frequency">Frequency</InputLabel>
                    <Input name="frequency" id="frequency" type="number"
                        value={this.props.frequency}
                        onChange={this.handleChangeInput}
                        />
                <div className="DatePickerBlock">

                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                        <Grid container justify="space-around">
                        <DatePicker
                            margin="normal"
                            label="Start interval"
                            value={start}
                            onChange={this.handleChangeDateStart}
                        />
                        
                        </Grid>
                    </MuiPickersUtilsProvider>
                    <Button size="small" mini={true} onClick={this.clearStart} variant="contained" color="secondary">Clear</Button>
                </div>
                <div className="DatePickerBlock">

                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                        <Grid container justify="space-around">
                        <DatePicker
                            margin="normal"
                            label="End interval"
                            value={end}
                            onChange={this.handleChangeDateEnd}
                        />
                        
                        </Grid>
                        <Button size="small" mini={true} onClick={this.clearEnd} variant="contained" color="secondary">Clear</Button>
                    </MuiPickersUtilsProvider>
                </div>
                <Button size="small" onClick={this.removeFilter} variant="contained" color="secondary">Remove filter</Button>
                </FormGroup>

            </div>
        )
    }
}

// Filter.propTypes = {
//     org: PropTypes.string
// }
