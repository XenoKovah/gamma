const gulp = require('gulp');
const sass = require('gulp-sass');
const concat       = require('gulp-concat');
const minify       = require('gulp-minify');
const cleanCss     = require('gulp-clean-css');
const clean        = require('gulp-clean');
const copy         = require('gulp-copy');
const run = require('gulp-run');
const autoprefixer    = require('gulp-autoprefixer');

const path = require('path');

const static = path.resolve(__dirname, '../../core/static/core');

gulp.task('pack-css', function () {
    return gulp.src(['build/static/css/*'])
        .pipe(concat('css/stylesheet.css'))
        .pipe(cleanCss())
        .pipe(gulp.dest(static));
});

gulp.task('pack-js', function () {
    return gulp.src(['build/static/js/*.js'])
      .pipe(concat('js/bundle.js'))
      .pipe(gulp.dest(static));
});

gulp.task('pack-scss', function () {
    return gulp.src(['assets/scss/**/*.scss'])
      .pipe(sass().on('error', sass.logError))
      .pipe(autoprefixer())
      .pipe(concat('css/admin-stylesheet.css'))
      .pipe(cleanCss())
      .pipe(gulp.dest(static));
});

gulp.task('sass:watch', function () {
    return gulp.watch('assets/scss/**/*.scss', gulp.series('pack-scss'));
});

gulp.task('build', () => {
    run('npm run build').exec()
    .pipe(gulp.dest('build'))
    .pipe(console.log('FINISH'))
});

gulp.task('default', gulp.series('pack-scss','pack-css', 'pack-js'));
