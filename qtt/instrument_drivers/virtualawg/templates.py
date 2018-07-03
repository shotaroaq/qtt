from qctoolkit.pulses import TablePT
from qctoolkit.pulses import FunctionPT


class DataTypes:
    """ The possible data types for the pulse creation."""
    RAW_DATA = 'RAW_DATA'
    QC_TOOLKIT = 'QC_TOOLKIT'


class Templates:

    @staticmethod
    def square(name):
        """ Creates a block wave QC toolkit template for sequencing.

        Arguments:
            name (str): The user defined name of the sequence.

        Returns:
            The template with the square wave.
        """
        return TablePT({name: [(0, 0), ('period/4', 'amplitude'), ('period*3/4', 0), ('period', 0)]})

    @staticmethod
    def sawtooth(name):
        """ Creates a sawtooth QC toolkit template for sequencing.

        Arguments:
            name (str): The user defined name of the sequence.

        Returns:
            The sequence with the sawtooth wave.
        """
        return TablePT({name: [(0, 0), ('period*(1-width)/2', '-amplitude', 'linear'),
                               ('period*(1-(1-width)/2)', 'amplitude', 'linear'), ('period', 0, 'linear')]})

    @staticmethod
    def hold(name):
        """Creates a DC offset QC toolkit template for sequencing.

        Arguments:
            name (str): The user defined name of the sequence.

        Returns:
            The sequence with the wait pulse.
        """
        return TablePT({name: [(0, 'offset'), ('holdtime', 'offset')]})

    @staticmethod
    def marker(name):
        """Creates a TTL pulse QC toolkit template for sequencing.

        Arguments:
            name (str): The user defined name of the sequence.

        Returns:
            The sequence with the wait pulse.
        """
        return TablePT({name: [(0, 0), ('period*offset', 1), ('period*(offset+uptime)', 0), ('period', 0)]})
    
    def sine(name):
        """ Creates a sine QC toolkit template for sequencing.

        Arguments:
            name (str): The user defined name of the sequence.

        Returns:
            The sequence with the sawtooth wave. Parameters are 'duration', 'omega' and 'amplitude'
        """
        template = FunctionPT('amplitude*sin(2*pi*omega*t/1e9)', '1e9*duration')    
        return template


def test_sequence_templates(fig=None):
    import matplotlib.pyplot as plt
    from qctoolkit.pulses import SequencePT, TablePT
    sq=Templates.square('square')
    seq=SequencePT( (sq, {'amplitude': .5, 'period': 1e-3}) )

    from qctoolkit.pulses.plotting import plot
    
    # 10 MHz for 1 ms
    template = FunctionPT('sin(2*pi*omega*t/1e9)', '1e9*duration')    
    
    if fig is not None:
        plt.figure(fig); plt.clf()
        _ = plot(template, {'omega': 10e6, 'duration': 1e-6}, sample_rate=10, axes=plt.gca())

if __name__=='__main__':
    test_sequence_templates(fig=10)
    