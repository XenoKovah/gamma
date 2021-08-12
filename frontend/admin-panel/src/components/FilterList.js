import React from 'react';
import TextField from '@material-ui/core/TextField';
import { MuiPickersUtilsProvider, DatePicker } from 'material-ui-pickers';
import DateFnsUtils from '@date-io/date-fns';


import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';

import Typography from '@material-ui/core/Typography';

export default class FilterList extends React.Component {

    renderFilter() {
        let filters = [];
        for ( let key in this.props.filters) {
            if (typeof this.props.filters[key] == 'object') {
                filters.push(
                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                        <DatePicker key={0} defaultValue={this.props.filters[key].start} disabled={true}/>
                        <DatePicker key={1} defaultValue={this.props.filters[key].end} disabled={true}/>
                    </MuiPickersUtilsProvider>
                )
            } else {
                filters.push(
                    <TextField defaultValue={this.props.filters[key]}  disabled={true}/>
                )
            }
        }
        return filters;
    }

    render() {
        let start = this.props.filters && this.props.filters.interval && this.props.filters.interval.start ? new Date(this.props.filters.interval.start).toDateString() : null;
        let end = this.props.filters &&  this.props.filters.interval && this.props.filters.interval.end ? new Date(this.props.filters.interval.end).toDateString() : null;
        let org = this.props.filters ? this.props.filters.org : null;
        let frequency = this.props.filters ? this.props.filters.frequency : null;
        let course = this.props.filters ? this.props.filters.course : null;
        return (
            <Paper>
                <Typography color="inherit" variant="subtitle1" className="TableHeading">
                    <h3>Filters</h3>
                </Typography>
                <Table>
                    <TableHead>
                    <TableRow>
                        <TableCell align="center">{gettext('Organisation')}</TableCell>
                        <TableCell align="center">{gettext('Course')}</TableCell>
                        <TableCell align="center">{gettext('Frequency')}</TableCell>
                        <TableCell align="center">{gettext('Interval')}</TableCell>
                    </TableRow>
                    </TableHead>
                    <TableBody>

                        <TableRow>
                        <TableCell align="center">{org}</TableCell>
                        <TableCell align="center">{course}</TableCell>
                        <TableCell align="center">{frequency}</TableCell>
                        <TableCell align="center">{start} - {end}</TableCell>
                        </TableRow>

                    </TableBody>
                </Table>
            </Paper>
        )
    }
}
