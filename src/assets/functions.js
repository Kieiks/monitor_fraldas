var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};

dagfuncs.MinObject = (obj) => {
    return Math.min(...Object.values(obj).filter((v) => {if (typeof(v) == 'number') { return v}}))
}

dagfuncs.MakeFloat = (params) => {
             params.data[params.column.colId] = parseFloat(params.newValue);
             return true;
         }

dagfuncs.TwoDecimalFormatter = (params) => {
    if (typeof params.value === "number") {
        return params.value.toFixed(2);
    }
    return params.value;
};