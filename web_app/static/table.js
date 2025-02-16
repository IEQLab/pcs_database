document.addEventListener("DOMContentLoaded", function () {
    console.log("Table.js loaded successfully!");

    $(document).ready(function () {
        let table = $('#dataTable').DataTable({
            scrollY: '500px',
            scrollX: true,
            scrollCollapse: true,
            paging: false,
            searching: true,
            ordering: true,
            fixedHeader: true
        });

        // Global search functionality
        $('#searchInput').on('keyup', function () {
            table.search(this.value).draw();
        });

//        // Populate column filters dynamically
//        table.on('init', function () {
//            console.log("DataTable initialized. Populating filters...");
//
//            $('#dataTable thead tr:eq(1) th').each(function (index) {
//                let select = $(this).find('select');
//
//                if (select.length) {
//                    let columnData = table.column(index).data().toArray().filter(value => value.trim() !== "");
//                    let uniqueValues = [...new Set(columnData)];
//
//                    uniqueValues.sort().forEach(value => {
//                        select.append(`<option value="${value}">${value}</option>`);
//                    });
//
//                    console.log(`Column ${index} filter values:`, uniqueValues);
//
//                    select.on('change', function () {
//                        let val = $.fn.dataTable.util.escapeRegex($(this).val());
//                        table.column(index).search(val ? `^${val}$` : '', true, false).draw();
//                    });
//                }
//            });
//        });
    });
});
